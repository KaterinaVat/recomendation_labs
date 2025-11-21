
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.keyboards.inline import model_choice_menu


router = Router() 

@router.message(Command("start"))
async def start_command_handler(message: Message) -> None:
    await message.answer(
        "Привет🧚🏻‍♀️! Я бот, который поможет тебе подготовиться к техническому собеседованию.🤍 \n\n" \
        "Ты можешь получить подсказки🎀, которые помогут тебе решить их🍒. \n\n" \
        "Выбери модель, с которой хочешь работать:",
        reply_markup=model_choice_menu
    )

