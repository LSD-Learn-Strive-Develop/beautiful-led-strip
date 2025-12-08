"""Message handlers for Telegram bot."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from aiogram import Router, F
from aiogram.types import Message

from src.led.symbols import (
    COLORS,
    RGB_COLORS,
    EMOJI_RAINBOW,
    EMOJI_TEMPERATURE,
    is_displayable,
)
from src.bot.keyboards import get_main_keyboard

if TYPE_CHECKING:
    from src.bot.app import AppContext

router = Router(name="messages")

# Rate limiting: user_id -> last_request_timestamp
_rate_limits: dict[int, float] = {}
RATE_LIMIT_SECONDS = 5.0


def _check_rate_limit(user_id: int) -> bool:
    """Check if user is within rate limit.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if request is allowed, False if rate limited
    """
    now = time.time()
    last_request = _rate_limits.get(user_id, 0)
    
    if now - last_request < RATE_LIMIT_SECONDS:
        return False
    
    _rate_limits[user_id] = now
    return True


@router.message(F.text, ~F.text.startswith("/"))
async def handle_message(message: Message, app_context: AppContext) -> None:
    """Handle all text messages.
    
    Processes color changes, mode switches, and text display requests.
    """
    if not message.text or not message.from_user:
        return
    
    user_id = message.from_user.id
    text = message.text
    
    # Rate limiting
    if not _check_rate_limit(user_id):
        await message.reply("Попробуй позже ⏳")
        return
    
    # Mode commands
    if text in ("main", "user", "fight"):
        app_context.display_manager.set_mode(text)
        await message.answer(f"Режим: {text}", reply_markup=get_main_keyboard())
        return
    
    # Color change via emoji
    if text in COLORS:
        color_name = COLORS[text]
        rgb = RGB_COLORS[color_name]
        
        app_context.display_manager.disable_rainbow()  # Turn off rainbow mode
        app_context.led_controller.set_color(rgb)
        app_context.color_storage.save_color(rgb)
        app_context.display_manager.request_refresh()
        
        await _notify_admin(message, app_context, f"изменил цвет {text}")
        await message.answer("Цвет изменён ✨", reply_markup=get_main_keyboard())
        return
    
    # Rainbow effect
    if text == EMOJI_RAINBOW:
        app_context.display_manager.show_rainbow()
        await message.answer("🌈", reply_markup=get_main_keyboard())
        return
    
    # Temperature display
    if text == EMOJI_TEMPERATURE:
        app_context.display_manager.show_temperature()
        await message.answer("🌡", reply_markup=get_main_keyboard())
        return
    
    # Text display (admin only)
    if is_displayable(text.upper()):
        if app_context.admin_manager.is_admin(user_id):
            app_context.display_manager.show_text(text.upper())
            await _notify_admin(message, app_context, f"показал текст: {text}")
            await message.answer("Текст отправлен 📝", reply_markup=get_main_keyboard())
        else:
            await message.answer(
                "Отправка текста доступна только администраторам",
                reply_markup=get_main_keyboard(),
            )
        return
    
    # Unknown command
    await message.answer(
        "Не понимаю. Отправь сердечко для смены цвета.",
        reply_markup=get_main_keyboard(),
    )


async def _notify_admin(
    message: Message,
    app_context: AppContext,
    action: str,
) -> None:
    """Send notification to admin about user action.
    
    Args:
        message: Original user message
        app_context: Application context
        action: Description of the action
    """
    admin_id = app_context.config.telegram.admin_id
    
    if not admin_id or message.from_user.id == admin_id:
        return
    
    try:
        username = message.from_user.username
        name = f"@{username}" if username else message.from_user.first_name
        
        await app_context.bot.send_message(
            admin_id,
            f"{name} {action}",
        )
    except Exception as e:
        print(f"Failed to notify admin: {e}")
