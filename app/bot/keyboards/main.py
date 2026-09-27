from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🧮 Рассчитать маржу"
                ),
            ],
            [
                KeyboardButton(
                    text="🗑 Очистить контекст"
                ),
            ],
        ],
        resize_keyboard=True,
    )