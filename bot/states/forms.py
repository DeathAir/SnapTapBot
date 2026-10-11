from aiogram.fsm.state import State, StatesGroup



class RegisterForm(StatesGroup):
    username = State()
    phone_choice = State()
    phone_confirm = State()
    phone_manual = State()