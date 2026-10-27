from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from PIL import Image
from pyzbar.pyzbar import decode
from urllib.parse import urlparse, parse_qs

from bot.api_client import ApiClient
from bot.keyboards import phone_choice_keyboard, phone_confirm_keyboard, get_main_menu
from bot.states.forms import RegisterForm
from config import settings

router = Router()


async def register_user(
        message: Message,
        state: FSMContext,
        api_client: ApiClient,
        phone: str,
) -> None:
    data = await state.get_data()
    username = data.get("username")
    telegram_id = message.from_user.id
    role = "superadmin" if telegram_id == settings.superadmin_id else "user"
    try:
        await api_client.get_or_create_user(
            telegram_id=telegram_id,
            username=username,
            phone=phone,
            role=role,
        )
        await message.answer(
            "✅ Ты зарегистрирован!",
            reply_markup=get_main_menu(role),
        )
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(Command("start"))
async def cmd_start(
        message: Message,
        state: FSMContext,
        api_client: ApiClient,
) -> None:
    telegram_id = message.from_user.id

    try:
        user = await api_client.get_user(telegram_id)
        role = user.get("role", "user")
        await message.answer(
            "С возвращением!",
            reply_markup=get_main_menu(role),
        )
    except Exception:
        await message.answer(
            "Привет! Давай зарегистрируемся.\n"
            "Шаг 1 из 2. Введи свой username:"
        )
        await state.set_state(RegisterForm.username)


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message, api_client: ApiClient) -> None:
    try:
        user = await api_client.get_user(message.from_user.id)
        role = user.get("role", "user")

        text = (
            "ℹ️ <b>Доступные команды:</b>\n\n"
            "/start — Главное меню\n"
            "/help — Эта справка\n"
            "/my_tickets — Мои билеты\n"
        )

        if role in ["admin", "superadmin"]:
            text += (
                "\n🛡 <b>Команды администратора:</b>\n"
                "/stats — Статистика клуба\n"
                "/users_club — Пользователи клуба\n"
                "/tickets_club — Билеты клуба\n"
                "/generate_tickets — Сгенерировать билеты\n"
                "/create_raffle — Создать розыгрыш (с призами)\n"
                "/hold_raffle — Провести розыгрыш\n"
                "/download_report — Скачать отчет\n"
            )

        if role == "superadmin":
            text += (
                "\n👑 <b>Команды супер-админа:</b>\n"
                "/list_users — Список всех пользователей\n"
                "/make_admin &lt;ID&gt; &lt;club_id&gt; — Выдать права админа\n"
                "/new_club — Создать новый клуб\n"
            )

        await message.answer(text, parse_mode="HTML")

    except Exception:
        await message.answer(
            "ℹ️ Доступные команды:\n"
            "/start\n"
            "/help\n"
            "/my_tickets"
        )


@router.message(RegisterForm.username)
async def process_username(
        message: Message,
        state: FSMContext,
) -> None:
    username = message.text.strip()

    if len(username) < 5 or len(username) > 55:
        await message.answer("Username должен быть от 5 до 55 символов. Попробуй ещё:")
        return

    await state.update_data(username=username)
    await message.answer(
        "Отлично! Шаг 2 из 2. Какой у тебя номер телефона?",
        reply_markup=phone_choice_keyboard(),
    )
    await state.set_state(RegisterForm.phone_choice)


@router.message(RegisterForm.phone_choice, F.text == "✏️ Ввести вручную")
async def process_phone_choice(message: Message, state: FSMContext) -> None:
    await message.answer("Введи номер, который дал в клубе. Формат: +7XXXXXXXXXX")
    await state.set_state(RegisterForm.phone_manual)


@router.message(RegisterForm.phone_choice, F.contact)
async def process_contact(message: Message, state: FSMContext) -> None:
    phone = message.contact.phone_number
    await state.update_data(shared_phone=phone)
    await message.answer(
        f"Ты поделился номером: {phone}\nЭто тот номер, который ты дал в клубе?",
        reply_markup=phone_confirm_keyboard(),
    )
    await state.set_state(RegisterForm.phone_confirm)


@router.message(RegisterForm.phone_confirm)
async def process_phone_confirm(message: Message, state: FSMContext, api_client: ApiClient) -> None:
    if message.text == "✅ Да":
        data = await state.get_data()
        phone = data.get("shared_phone")
        await register_user(message, state, api_client, phone)

    elif message.text == "❌ Нет, введу сам":
        await message.answer("Введите номер указанный в заведении:")
        await state.set_state(RegisterForm.phone_manual)

    else:
        await message.answer("Пожалуйста, нажми на кнопку на клавиатуре.")


@router.message(RegisterForm.phone_manual)
async def process_phone_manual(message: Message, state: FSMContext, api_client: ApiClient) -> None:
    phone = message.text.strip()
    if not phone.startswith("+") or not phone[1:].isdigit() or not (11 <= len(phone) <= 16):
        await message.answer("Неверный формат. Введи номер в формате +79991234567")
        return
    await register_user(message, state, api_client, phone)


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Регистрация отменена. Напиши /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove()
    )


# Билеты

@router.message(Command("my_tickets"))
@router.message(F.text == "🎫 Мои билеты")
async def cmd_my_tickets(message: Message, api_client: ApiClient) -> None:
    try:
        data = await api_client.get_my_tickets(message.from_user.id)
    except Exception as e:
        await message.answer(f"Не удалось загрузить билеты. Ошибка: {e}")
        return

    tickets = data.get("tickets", [])

    if not tickets:
        await message.answer("У тебя пока нет билетов.")
        return

    text = "🎫 Твои билеты:\n\n"

    for ticket in tickets:
        number = ticket.get("number")
        text += f"Билет №{number}\n"

    await message.answer(text)


# --- ПРОВЕРКА QR-КОДА ---

@router.message(F.photo)
async def process_photo(message: Message, bot: Bot, api_client: ApiClient) -> None:

    file_id = message.photo[-1].file_id
    file = await bot.download(file_id)

    try:

        img = Image.open(file)
        decoded_data = decode(img)

        if not decoded_data:
            await message.answer("QR-код не распознан. Отправь фото ближе/качественнее.")
            return


        qr_text = decoded_data[0].data.decode("utf-8")


        parsed_url = urlparse(qr_text)
        params = parse_qs(parsed_url.query)

        ticket_number = int(params.get("ticket")[0])
        secret_hash = params.get("hash")[0]
        club_id = int(params.get("club")[0])


        user = await api_client.get_user(message.from_user.id)
        user_id = user.get("id")


        result = await api_client.verify_ticket(
            number=ticket_number,
            secret_hash=secret_hash,
            club_id=club_id,
            user_id=user_id,
            telegram_id=message.from_user.id
        )


        if result.get("status") == "success":

            await message.answer(result.get("message"))
        else:
            await message.answer(result.get("message"))

    except Exception as e:
        await message.answer(f"❌ Ошибка при проверке билета: {e}")