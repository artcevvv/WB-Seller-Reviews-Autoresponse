from aiogram import types

from components.config import *
from components.keyboards import *
from components.database import *

from components.bot_components.options import *

@dp.callback_query_handler(lambda c: c.data == "tokens")
async def tokens_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id
    keyboard = tokens_kb_layout()

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=original_message_id,
        text="⬇️ Выберите действие: ",
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == "buy")
async def proccess_buy_comma(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    if TRANZZO_TEST_PAYMENT.split(":")[1] == "TEST":
        await bot.send_message(
            chat_id, text="❗️ Тестовая оплата! Карта: 4242 4242 4242 4242"
        )

    keyboard = InlineKeyboardMarkup(row_width=1)

    for option in POINTS_PRICES:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{option['description']}", callback_data=f"buy_{option['amount']}"
            )
        )

    await bot.send_message(
        chat_id=chat_id,
        text="Выберите количество токенов, которое желаете приобрести.",
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == "what_is")
async def handle_what_is_button(callback_query: types.CallbackQuery):
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


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("buy_"))
async def handle_buy_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    package_amount = int(callback_query.data.split("_")[1])  # Corrected splitting

    selected_package = next(
        (p for p in POINTS_PRICES if p["amount"] == package_amount), None
    )

    if not selected_package:
        await bot.answer_callback_query(
            callback_query.id, text="Произошла ошибка при покупке токенов!"
        )
        return

    await bot.send_invoice(
        chat_id=user_id,
        title=f"{selected_package['amount']} токенов",
        description=f"Покупка {selected_package['amount']} токенов",
        provider_token=TRANZZO_TEST_PAYMENT,
        currency="KZT",
        prices=[
            {
                "label": f"{selected_package['amount']} токенов",
                "amount": selected_package["price"] * 100,
            }
        ],
        payload=f"buy_tokens_{selected_package['amount']}",
    )

    await bot.answer_callback_query(callback_query.id)


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    user_id = message.chat.id
    payload = message.successful_payment.invoice_payload

    # Correctly split the payload and access the index
    parts = payload.split("_")
    if len(parts) < 3:
        await message.reply("❌ Ошибка в данных платежа.")
        return

    try:
        token_amount = int(parts[2])
    except ValueError:
        await message.reply("❌ Ошибка в данных платежа.")
        return

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()

        if user:
            user.points += token_amount
            session.commit()

            await message.reply(
                f"✅ Покупка успешна! Вы получили {token_amount} токенов. У вас теперь {user.points} токенов."
            )
        else:
            await message.reply("❌ Пользователь не найден.")