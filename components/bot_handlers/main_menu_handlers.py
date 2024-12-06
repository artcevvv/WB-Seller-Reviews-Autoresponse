from aiogram import types
import asyncio

from components.config import *
from components.database import *
from components.bot import *
from components.keyboards import *
from components.fetch import *

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class APIKeyForm(StatesGroup):
    waiting_for_api_key = State()


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
                    "❌ У вас недостаточно токенов для ответа. Пожалуйста, пополните баланс.",
                )
                return
            elif not user or not user.tokens:
                logging.info(f"No user or tokens found for user ID: {user_id}")
                await bot.send_message(
                    user_id,
                    "❌ Необходимо добавить хотя бы один API токен!",
                    parse_mode=ParseMode.HTML,
                )
                return

            # Запускаем fetch_reviews в фоновом режиме
            asyncio.create_task(fetch_reviews(user_id, kb_layout))
    except Exception as e:
        logging.info(f"Error handling answer command: {e}")


@dp.callback_query_handler(lambda c: c.data == "add_api")
async def add_api_handler(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id
    original_message_id = callback_query.message.message_id

    keyboard = contact_keyboard()

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == chat_id).first()

        if not user or not user.phone_number:
            await callback_query.message.reply(
                "❌ Вы не зарегистрированы! Отправьте мне свой контакт, чтобы зарегистрироваться.",
                reply_markup=keyboard,
            )
            return
        else:
            await bot.edit_message_text(
                text="✒️ Введите свой API-ключ продавца.\nДля отмены введите команду '/cancel'",
                chat_id=chat_id,
                message_id=original_message_id,
                reply_markup=None,
            )

    # Set the state to waiting for API key
    await state.set_state(APIKeyForm.waiting_for_api_key.state)
    logger.info(f"State set to APIKeyForm.waiting_for_api_key for user {chat_id}")


@dp.message_handler(commands="cancel", state="*")
async def cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

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
        user = (
            session.query(User)
            .filter(User.telegram_user_id == telegram_user_id)
            .first()
        )
        token = Token(
            user_id=user.id, wb_token=api_key, telegram_user_id=telegram_user_id
        )
        session.add(token)
        session.commit()

        await message.reply("✅ API ключ успешно сохранен!")
        await message.delete()

    await state.finish()


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
    keyboard = settings_kb()
    await bot.edit_message_text(
        text="⬇️ Выберите действие: ",
        chat_id=chat_id,
        message_id=original_message_id,
        reply_markup=keyboard,
    )


@dp.callback_query_handler(lambda c: c.data == "delete_token")
async def delete_token_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    orig_msg = callback_query.message.message_id
    user_id = callback_query.from_user.id

    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_user_id == user_id).first()

        if user and user.tokens:
            kb = InlineKeyboardMarkup(row_width=1)
            for token in user.tokens:
                kb.add(
                    InlineKeyboardButton(
                        f"🗑 Удалить токен {token.wb_token[:10]}...",
                        callback_data=f"delete_token_{token.id}",
                    )
                )

            await bot.edit_message_text(
                "⬇️ Выберите какой токен вы хотите удалить:",
                chat_id=chat_id,
                message_id=orig_msg,
                reply_markup=kb,
            )
        else:
            await bot.edit_message_text(
                text="❌ У вас нет токенов!", chat_id=chat_id, message_id=orig_msg
            )


@dp.callback_query_handler(lambda c: c.data.startswith("delete_token_"))
async def confirm_delete_token_handler(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    orig_msg = callback_query.message.message_id
    user_id = callback_query.from_user.id

    try:
        parts = callback_query.data.split("_")
        if len(parts) < 3 or not parts[2].isdigit():
            raise ValueError("Invalid callback data format")

        token_id = int(parts[2])
        # logging.warning(f"Attempting to delete token_id={token_id} for user_id={user_id}")

        with SessionLocal() as session:
            token_to_delete = (
                session.query(Token)
                .filter(Token.id == token_id, Token.telegram_user_id == user_id)
                .first()
            )

            if token_to_delete:
                # logging.debug(f"Found token with token_id={token_id}. token_to_delete.user_id={token_to_delete.telegram_user_id}")

                # Check if token is linked to the current user
                if token_to_delete.telegram_user_id == user_id:
                    session.delete(token_to_delete)
                    session.commit()

                    await bot.edit_message_text(
                        text="✅ Токен успешно удален!",
                        chat_id=chat_id,
                        message_id=orig_msg,
                    )
                else:
                    # logging.warning(f"User ID mismatch: token's user_id={token_to_delete.telegram_user_id}, expected user_id={user_id}")
                    await bot.edit_message_text(
                        text="⚠️ Токен не найден или у вас нет разрешения для его удаления! \n\n🆘 Обратитесь за помощью к разработчику: @jeixblehh",
                        chat_id=chat_id,
                        message_id=orig_msg,
                    )
            else:
                # logging.warning("Token not found by ID")
                await bot.edit_message_text(
                    text="⚠️ Токен не найден или у вас нет разрешения для его удаления! \n\n🆘 Обратитесь за помощью к разработчику: @jeixblehh",
                    chat_id=chat_id,
                    message_id=orig_msg,
                )

    except ValueError as e:
        logging.error(f"Error in callback data format: {e}")
        await bot.edit_message_text(
            text="⚠️ Произошла ошибка! Неверный формат данных.",
            chat_id=chat_id,
            message_id=orig_msg,
        )


@dp.callback_query_handler(lambda c: c.data == "delete_account")
async def delete_account_handler(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    orig_message = cq.message.message_id
    chat_id = cq.message.chat.id
    kb = yesno_kb()

    await bot.edit_message_text(
        text="❓ Вы точно хотите удалить свой аккаунт?",
        chat_id=chat_id,
        message_id=orig_message,
        reply_markup=kb,
    )


@dp.callback_query_handler(lambda c: c.data == "confirm_btn")
async def confirm_delete_acc(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    orig_message = cq.message.message_id
    chat_id = cq.message.chat.id

    with SessionLocal() as s:
        user_to_del = s.query(User).filter(User.telegram_user_id == user_id).first()

        if user_to_del:
            s.delete(user_to_del)
            s.commit()

            await bot.edit_message_text(
                text="✅ Аккаунт успешно удален. \n\n🆘 Если у вас есть предложения- обратитесь к разработчику: @jeixblehh",
                chat_id=chat_id,
                message_id=orig_message,
            )
        else:
            await bot.edit_message_text(
                text="❌ Аккаунт не был удален! \n\n🆘 Обратитесь за помощью к разработчику: @jeixblehh",
                chat_id=chat_id,
                message_id=orig_message,
            )
