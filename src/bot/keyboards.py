"""Telegram keyboard layouts."""

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

from src.led.symbols import COLORS, EMOJI_RAINBOW, EMOJI_TEMPERATURE, EMOJI_SLOTS


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Create main control keyboard with color and action buttons.
    
    Returns:
        Configured reply keyboard markup
    """
    builder = ReplyKeyboardBuilder()
    
    # Add color buttons
    for emoji in COLORS.keys():
        builder.button(text=emoji)
    
    # Add action buttons (temperature, rainbow, slots)
    builder.button(text=EMOJI_TEMPERATURE)
    builder.button(text=EMOJI_RAINBOW)
    builder.button(text=EMOJI_SLOTS)
    
    # Layout: 3 columns for colors, 3 for actions
    builder.adjust(3, 3, 3, 3)
    
    return builder.as_markup(resize_keyboard=True)
