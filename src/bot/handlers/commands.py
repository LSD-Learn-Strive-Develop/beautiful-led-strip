"""Command handlers for Telegram bot."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .keyboards import get_main_keyboard

router = Router(name="commands")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command.
    
    Sends welcome message with control keyboard.
    """
    await message.reply(
        "Привет! 👋\n\n"
        "Отправляй мне эмодзи-сердечки и я буду менять цвет ленты "
        "в цвет отправленного сердечка.\n\n"
        "🌈 — радуга\n"
        "🌡 — температура",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    await message.reply(
        "Доступные команды:\n\n"
        "/start — начать работу\n"
        "/help — эта справка\n\n"
        "Отправь сердечко чтобы изменить цвет, "
        "или напиши текст (только для админов).",
        reply_markup=get_main_keyboard(),
    )
