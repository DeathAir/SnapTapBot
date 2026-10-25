from aiogram import Router, F
from aiogram.filters import Command

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import api_client
from bot.api_client import ApiClient
from bot.states.forms import ClubCreateForm, DeleteClubForm
from config import settings

router = Router()

@router.message(Command("club_manage"))
@router.message(F.text == "👑 Управление клубами")
async def cmd_manage_clubs(message: Message, api_client: ApiClient):
    try:
        clubs = await api_client.get_all_clubs()

        active_clubs = [c for c in clubs if c.get('is_active')]

        if not active_clubs:
            await message.answer("В базе пока нет активных клубов.")
            return

        text = "🏢 Все клубы:\n\n"
        for c in active_clubs:
            text += f"ID: {c.get('id')} | {c.get('name')}\n"

        text += "\nЧтобы создать новый клуб, напиши /new_club"
        await message.answer(text)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(Command("new_club"))
async def cmd_new_club(message: Message, state: FSMContext):
    await message.answer("Введите название заведения:")
    await state.set_state(ClubCreateForm.name)


@router.message(ClubCreateForm.name)
async def process_club_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите адрес заведения:")
    await state.set_state(ClubCreateForm.address)


@router.message(ClubCreateForm.address)
async def process_club_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите номер телефона заведения:")
    await state.set_state(ClubCreateForm.phone)


@router.message(ClubCreateForm.phone)
async def process_club_phone(message: Message, state: FSMContext, api_client: ApiClient):
    try:
        await state.update_data(phone=message.text)
        data = await state.get_data()

        result = await api_client.create_club(
            name=data.get('name'),
            address=data.get('address'),
            phone=data.get('phone'),
            is_active=True
        )
        await message.answer(f"✅ Клуб '{result.get('name')}' создан! ID: {result.get('id')}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
    finally:
        await state.clear()

@router.message(Command("overall_progress"))
@router.message(F.text == "📈 Общая статистика")
async def cmd_superadmin_stats(message: Message, api_client: ApiClient):  # ← Новое имя функции
    try:
        stats = await api_client.get_superadmin_stats()

        text = (
            f"📈 Глобальная статистика:\n\n"
            f"🏢 Всего клубов: {stats.get('total_clubs')} (Активных: {stats.get('active_clubs')})\n"
            f"👥 Всего пользователей: {stats.get('total_users')}\n"
            f"🎫 Всего билетов: {stats.get('total_tickets')}\n"
            f"✅ Зарегистрировано билетов: {stats.get('total_registered')}\n"
            f"🔥 Общий прогресс: {stats.get('overall_progress')}%"
        )

        await message.answer(text)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

@router.message(Command("delete_club"))
@router.message(F.text == "❌ Удалить клуб")
async def process_superadmin_clubs(message: Message, state: FSMContext):
    await message.answer("Введите ID клуба для удаления:")
    await state.set_state(DeleteClubForm.club_id)

@router.message(DeleteClubForm.club_id)
async def process_delete_club(message: Message, state: FSMContext, api_client: ApiClient):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи число (ID розыгрыша):")
        return

    club_id = int(message.text)
    try:
        await message.answer("Процесс удаления....")

        result = await api_client.delete_club(club_id)
        await message.answer("✅ Клуб успешно удален!")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
    finally:
        await state.clear()

@router.message(Command("make_admin"))
async def make_admin(message: Message, api_client: ApiClient):
    if message.from_user.id != settings.superadmin_id:
        await message.answer("⛔ У тебя нет прав")
        return
    parts = message.text.split()

    if len(parts) != 3:
        await message.answer(
            "❌ Неверный формат команды.\n"
            "Используй: <code>/make_admin &lt;telegram_id&gt; &lt;club_id&gt;</code>\n"
            "Пример: <code>/make_admin 123456789 2</code>",
            parse_mode="HTML"
        )
        return

    try:
        target_telegram_id = int(parts[1])
        club_id = int(parts[2])
    except ValueError:
        await message.answer("❌ Ошибка: ID пользователя и номер клуба должны быть числами.")
        return

    try:
        await api_client.update_user(
            telegram_id=target_telegram_id,
            role="admin",
            club_id=club_id
        )
        await message.answer(
            f"✅ Успешно!\nПользователь <code>{target_telegram_id}</code> теперь Админ клуба <code>{club_id}</code>.",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")


@router.message(Command("list_users"))
async def cmd_list_users(message: Message, api_client: ApiClient):

    if message.from_user.id != settings.superadmin_id:
        await message.answer("⛔ У тебя нет прав.")
        return

    try:
        users = await api_client.get_all_users()

        if not users:
            await message.answer("В базе пока нет пользователей.")
            return

        text = "👥 <b>Список всех пользователей:</b>\n\n"

        for u in users:
            username = u.get('username', 'без_ника')
            tg_id = u.get('telegram_id')
            role = u.get('role')
            club_id = u.get('club_id')

            text += (
                f"👤 @{username}\n"
                f"🆔 ID: <code>{tg_id}</code>\n"
                f"👑 Роль: {role} | Клуб: {club_id}\n"
                f"➖➖➖➖➖➖➖➖\n"
            )

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"Ошибка: {e}")

