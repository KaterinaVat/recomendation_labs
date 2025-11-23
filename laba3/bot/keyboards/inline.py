from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ура-ура!🪇")]
    ],
    resize_keyboard=True
)

choice_buttons = InlineKeyboardBuilder()
choice_buttons.add(
    InlineKeyboardButton(text="Да🐒", callback_data="yes"),
    InlineKeyboardButton(text="Нет🙊", callback_data="no")
)
choice_buttons = choice_buttons.as_markup() 

like_or_dislike = InlineKeyboardBuilder()
like_or_dislike.add(
    InlineKeyboardButton(text="👍🏼", callback_data="like"),
    InlineKeyboardButton(text="👎🏼",  callback_data="dislike")
)
like_or_dislike = like_or_dislike.as_markup() 


index_group_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ladieswear")],
        [KeyboardButton(text="Menswear")],
        [KeyboardButton(text="Divided")],
        [KeyboardButton(text="Baby/Children")],
        [KeyboardButton(text="Sport")]
    ],
    resize_keyboard=True
)

product_group_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Garment Upper body")],
        [KeyboardButton(text="Underwear")],
        [KeyboardButton(text="Garment Lower body")],
        [KeyboardButton(text="Accessories")],
        [KeyboardButton(text="Nightwear")],
        [KeyboardButton(text="Swimwear")],
        [KeyboardButton(text="Underwear")],
        [KeyboardButton(text="Garment Full body")],
        [KeyboardButton(text="Shoes")],
        [KeyboardButton(text="Bags")]
    ],
    resize_keyboard=True
)

category_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Индекс")],
        [KeyboardButton(text="Тип")]
    ],
    resize_keyboard=True
)








