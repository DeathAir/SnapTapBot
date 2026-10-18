from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu(role: str) -> ReplyKeyboardMarkup:

    keyboard = [
        [KeyboardButton(text="🎫 Мои билеты")],
        [KeyboardButton(text="ℹ️ Помощь")],
    ]

    if role in "admin":
        keyboard.insert(0, [KeyboardButton(text="📊 Статистика")])
        keyboard.insert(1, [KeyboardButton(text="👥 Пользователи клуба")])
        keyboard.insert(2, [KeyboardButton(text="🎟 Билеты клуба")])
        keyboard.insert(3, [KeyboardButton(text="🎲 Создать розыгрыш")])
        keyboard.insert(4, [KeyboardButton(text="🎟 Сгенерировать билеты")])
        keyboard.insert(5, [KeyboardButton(text="🏆 Провести розыгрыш")])
        keyboard.insert(6, [KeyboardButton(text="📄 Скачать отчет")])



    if role == "superadmin":
        keyboard.insert(0, [KeyboardButton(text="📈 Общая статистика")])
        keyboard.insert(1, [KeyboardButton(text="👑 Управление клубами")])
        keyboard.insert(2, [KeyboardButton(text="❌ Удалить клуб")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def phone_choice_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True), KeyboardButton(text="✏️ Ввести вручную")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def phone_confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Да"),
                KeyboardButton(text="❌ Нет, введу сам"),
            ],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )