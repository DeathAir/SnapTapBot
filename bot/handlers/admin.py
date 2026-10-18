

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile

from bot import api_client
from bot.api_client import ApiClient
from bot.states.forms import GenerateTicketForm, RaffleCreateForm

router = Router()

@router.message(F.text == "📊 Статистика")
async def stats_msg(message: Message, api_client: ApiClient):
    try:
        user = await api_client.get_user(message.from_user.id)
        role = user.get("role")
        if role not in ["admin", "superadmin"]:
            await message.answer("⛔ У тебя нет прав")
            return

        club_id = user.get("club_id")
        stats = await api_client.get_stats(club_id)

        text = (
            f"📊 Статистика клуба:\n\n"
            f"Всего билетов: {stats.get('total_ticket')}\n"
            f"Осталось: {stats.get('remaining_ticket')}\n"
            f"Прогресс: {stats.get('progress_percent')}%"
        )
        await message.answer(text)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

@router.message(F.text == "🎟 Сгенерировать билеты")
async def generate_start(message: Message, state: FSMContext, api_client: ApiClient):
    try:
        user = await api_client.get_user(message.from_user.id)
        club_id = user.get("club_id")

        raffles = await api_client.get_club_raffles(club_id)

        if not raffles:
            await message.answer("В твоем клубе пока нет розыгрышей. Сначала создай хотя бы один!")
            return

        text = "Доступные розыгрыши\n\n"
        for r in raffles:
            text += f"🆔 ID: {r.get('id')} | {r.get('title')} (Приз: {r.get('prize')})\n"
        text += "\nВведи ID розыгрыша, для которого нужно создать билеты:"

        await message.answer(text)
        await state.set_state(GenerateTicketForm.raffle_id)
    except Exception as e:
        await message.answer(f"Ошибка при получении розыгрышей: {e}")

@router.message(GenerateTicketForm.raffle_id)
async def generate_get_raffle(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи число (ID розыгрыша):")
        return
    await state.update_data(raffle_id=int(message.text))
    await message.answer("Сколько билетов создать? (Введите число: )")
    await state.set_state(GenerateTicketForm.count)

@router.message(GenerateTicketForm.count)
async def generate_count(message: Message, state: FSMContext, api_client: ApiClient):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число (количество билетов):")
        return
    count = int(message.text)
    data = await state.get_data()
    raffle_id = data.get("raffle_id")

    try:
        user = await api_client.get_user(message.from_user.id)
        club_id = user.get("club_id")

        result = await api_client.generate_tickets(
            club_id=club_id,
            raffle_id=raffle_id,
            count=count
        )

        await message.answer(f"✅ {result.get('message')}\n⏳ Формирую архив с QR-кодами...")

        zip_bytes = await api_client.get_tickets_zip(club_id)

        # 3. Отправляем файл в Телеграм
        document = BufferedInputFile(zip_bytes, filename=f"tickets_club_{club_id}.zip")
        await message.answer_document(
            document=document,
            caption="📦 Вот твои QR-коды для печати!"
        )

    except Exception as e:
        await message.answer(f"Ошибка генерации: {e}")
    finally:
        await state.clear()


@router.message(F.text == "🎲 Создать розыгрыш")
async def cmd_create_raffle(message: Message, state: FSMContext):
    await message.answer("Введите название розыгрыша")
    await state.set_state(RaffleCreateForm.title)


@router.message(RaffleCreateForm.title)
async def process_raffle_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введи описание розыгрыша:")
    await state.set_state(RaffleCreateForm.description)


@router.message(RaffleCreateForm.description)
async def process_raffle_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите главный приз (если их несколько, перечисли через запятую):")
    await state.set_state(RaffleCreateForm.prize)


@router.message(RaffleCreateForm.prize)
async def process_raffle_prize(message: Message, state: FSMContext):
    await state.update_data(prize=message.text)
    await message.answer("Введи дату начала в формате ГГГГ-ММ-ДД:")
    await state.set_state(RaffleCreateForm.start_date)


@router.message(RaffleCreateForm.start_date)
async def process_raffle_start_date(message: Message, state: FSMContext):
    await state.update_data(start_date=message.text)
    await message.answer("Введите дату окончания в формате ГГГГ-ММ-ДД:")
    await state.set_state(RaffleCreateForm.end_date)


@router.message(RaffleCreateForm.end_date)
@router.message(RaffleCreateForm.end_date)
async def process_raffle_end_date(message: Message, state: FSMContext, api_client: ApiClient):
    try:
        await state.update_data(end_date=message.text)

        data = await state.get_data()

        user = await api_client.get_user(message.from_user.id)
        club_id = user.get("club_id")

        start_iso = f"{data.get('start_date')}T00:00:00"
        end_iso = f"{data.get('end_date')}T23:59:59"

        result = await api_client.create_raffle(
            user_id=message.from_user.id,
            title=data.get('title'),
            description=data.get('description'),
            prize=data.get('prize'),
            start_date=start_iso,
            end_date=end_iso,
            club_id=club_id
        )
        await message.answer(f"✅ Розыгрыш '{result.get('title')}' создан! ID: {result.get('id')}")
    except Exception as e:
        await message.answer(f"Ошибка создания розыгрыша: {e}")
    finally:
        await state.clear()





