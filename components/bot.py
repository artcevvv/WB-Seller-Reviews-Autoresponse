from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import logging

from components.database import *
from components.keyboards import *
from components.fetch import fetch_reviews
from components.config import *
from components.messages import *

from components.bot_components.options import *


class APIKeyForm(StatesGroup):
    waiting_for_api_key = State()


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.chat.id
    active_users.add(user_id)

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()

        if user:
            menu_layout = create_menu_keyboard()
            await message.reply("⬇️ Выберите действие"
                                f"У тебя {user.points}\n",
                                reply_markup=menu_layout)
        else:
            contact_layout = contact_keyboard()
            user = User(telegram_user_id=user_id, points = 10)
            session.add(user)
            session.commit()
            await message.reply(
                "Привет!👋 Я помогу тебе упростить ответы на отзывы Wildberries.\n"
                "Пожалуйста, отправь мне свой контакт, чтобы я мог тебя зарегистрировать.\n"
                f"У тебя {user.points}",
                reply_markup=contact_layout,
            )


@dp.callback_query_handler(lambda c: c.data == "next")
async def next_command(callback_query: types.CallbackQuery):
    original_message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    keyboard = create_menu_keyboard()

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        text="⬇️ Выберите действие",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == "answer")
async def answer_command(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    kb_layout = review_answer_keyboard()
    try:
        logging.info(f"Handling callback query for user: {user_id}")
        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_user_id == user_id).first()
            
            if user.points <= 0:
                await bot.send_message(
                    user_id,
                    "❌ У вас недостаточно токенов для ответа. Пожалуйста, пополните баланс."
                )
                return
            await fetch_reviews(user_id, kb_layout)
    except Exception as e:
        logging.info({e})


@dp.callback_query_handler(lambda c: c.data == "reply")
async def reply_command(callback_query: types.CallbackQuery):
    original_message_id = callback_query.message.message_id
    await bot.answer_callback_query(callback_query.id)
    review_id = message_to_review_map.get(
        original_message_id, "Review ID is not stored!"
    )
    await bot.send_message(callback_query.from_user.id, f"{review_id}")


from aiogram import types
from aiogram.dispatcher import FSMContext
import logging

logger = logging.getLogger(__name__)

@dp.callback_query_handler(lambda c: c.data == "add_api")
async def add_api_handler(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_user_id = callback_query.message.chat.id
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = contact_keyboard()

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()

        if not user or not user.phone_number:
            await callback_query.message.reply(
                "❌ Вы не зарегистрированы! Отправьте мне свой контакт, чтобы зарегистрироваться.",
                reply_markup=keyboard,
            )
            return
        else:
            await bot.edit_message_text(
                text="Введите свой API-ключ продавца.\nДля отмены введите команду '/cancel'",
                chat_id=chat_id,
                message_id=original_message_id,
                reply_markup=None,
            )

    # Set the state to waiting for API key
    await state.set_state(APIKeyForm.waiting_for_api_key.state)
    logger.info(f"State set to APIKeyForm.waiting_for_api_key for user {telegram_user_id}")

@dp.message_handler(commands='cancel', state='*')
async def cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    print(current_state) # Debug
    
    if current_state is None:
        await message.reply("❓ Нечего отменять.")
        

    await state.finish()
    await message.reply("✅ Операция успешно отменена.")

@dp.message_handler(state=APIKeyForm.waiting_for_api_key)
async def store_key(message: types.Message, state: FSMContext):
    telegram_user_id = message.chat.id
    api_key = message.text


    with SessionLocal() as session:
        if len(api_key) < 300:
            await message.answer(
                "❌ API ключ должен содержать не менее 300 символов. Пожалуйста, отправьте корректный API ключ."
            )
            return
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        token = Token(user_id=user.id, wb_token=api_key)
        session.add(token)
        session.commit()

        await message.reply("✅ API ключ успешно сохранен!")
        await message.delete()

    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "prev_button")
async def prev_button_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = create_menu_keyboard()
    await bot.edit_message_text(
        text="⬇️ Выберите действие",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == "howto")
async def howto_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = prev_keyboard()
    text = "📃 Для авторизации в сервисе требуется токен Wildberries, который действует 180 дней после его создания.\n\n Для создания токена:\n1. В личном кабинете нажмите на имя профиля и выберите <a href='https://seller.wildberries.ru/supplier-settings/access-to-api'>Настройки → Доступ к API.</a>\n2. Выберите категорию 'Вопросы и отзывы'\n3. Нажмите <b>Создать токен</b>\n4. Скопируйте и отправьте токен боту, выбрав в меню опцию 'Добавить API ключ'."
    await bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


@dp.callback_query_handler(lambda c: c.data == "settings")
async def setting_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = prev_keyboard()
    # text= ""
    await bot.edit_message_text(
        text="❌ Функция еще не готова!",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.message_handler(commands=["buy"])
async def proccess_buy_comma(message: types.Message):
    if TRANZZO_TEST_PAYMENT.split(":")[1] == "TEST":
        await bot.send_message(message.chat.id, text="test")
        
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for option in POINTS_PRICES:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{option['description']}",    
                callback_data=f"buy_{option['amount']}"
            )
        )

    # await bot.send_invoice( 
    #     message.chat.id,
    #     title="1000 токенов",
    #     description="1000 токенов",
    #     provider_token=TRANZZO_TEST_PAYMENT,
    #     prices=[PRICE],
    #     currency="kzt",
    #     payload= 'some-invoice-payload-for-our-internal-us'
    # )
    
    await message.reply(
        "Выберите количество токенов, которое желаете приобрести.",
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("buy_"))
async def handle_buy_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    package_amount = int(callback_query.data.split("_"[1]))
    
    selected_package = next((p for p in POINTS_PRICES if p["amount"] == package_amount), None)
    
    if not selected_package:
        await bot.answer_callback_query(callback_query.id, text="Произошла ошибка при покупке токенов!")
        return

    bot.send_invoice(
        chat_id=user_id,
        title=f"{selected_package['amount']} токенов",
        description=f"Покупка {selected_package} токенов",
        provider_token=TRANZZO_TEST_PAYMENT,
        currency="KZT",
        prices=[{"label": f"{selected_package['amount']} токенов", "amount": selected_package['price'] * 100}],
        payload=f"buy_tokens_{selected_package['amount']}"
    )
    
    await bot.answer_callback_query(callback_query.id)
    
@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    user_id = message.chat.id
    payload = message.successful_payment.invoice_payload
    
    token_amount = int(payload.split("_"[2]))
    
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()
        
        if user:
            user.points += token_amount
            session.commit()
            
            await message.reply(
                f"✅ Покупка успешна! Вы получили {token_amount} токенов. У вас теперь {user.tokens} токенов."
            ) 
        else:
            await message.reply("❌ Пользователь не найден.")

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_handler(message: types.Message):
    contact = message.contact
    user_id = message.chat.id
    # original_message_id = message.message_id
    keyboard = go_to_menu_keyboard()

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()
        if user and user.phone_number:
            await message.reply(
                "❌ Вы уже добавили свой номер телефона!", reply_markup=keyboard
            )
        else:
            user.phone_number = contact.phone_number
            session.commit()
            await message.reply(
                "✅ Спасибо! Ваш номер телефона сохранен.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await message.answer("⬇️ Выберите действие:", reply_markup=keyboard)


@dp.errors_handler()
async def handle_errors(update, exception):
    logging.error(f"Сообщение {update} вызвало ошибку {exception}")
    return True
