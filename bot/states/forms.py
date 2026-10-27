from aiogram.fsm.state import State, StatesGroup



class RegisterForm(StatesGroup):
    username = State()
    phone_choice = State()
    phone_confirm = State()
    phone_manual = State()

class GenerateTicketForm(StatesGroup):
    raffle_id = State()
    count = State()

class RaffleCreateForm(StatesGroup):
    title = State()
    description = State()
    prizes_count = State()
    current_prize = State()
    start_date = State()
    end_date = State()

class ClubCreateForm(StatesGroup):
    name = State()
    address = State()
    phone = State()

class DrawRaffleForm(StatesGroup):
    raffle_id = State()

class DeleteClubForm(StatesGroup):
    club_id = State()
