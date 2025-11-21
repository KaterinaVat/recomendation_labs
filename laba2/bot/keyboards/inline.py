from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

model_choice_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Llama")],
        [KeyboardButton(text="GPT")]
    ],
    resize_keyboard=True
)

aim_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Хочу разобраться в задачке")],
        [KeyboardButton(text="Проверь моё решение")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

continue_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Супер! Мне всё понятно")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)