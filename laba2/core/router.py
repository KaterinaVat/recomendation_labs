from aiogram import Router
from bot.handlers.start import router as start_router
from bot.handlers.message import router as message_router

router = Router()
router.include_router(start_router)
router.include_router(message_router)