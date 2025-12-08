"""Telegram keyboard layouts."""

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

from src.led.symbols import COLORS, EMOJI_RAINBOW, EMOJI_TEMPERATURE


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Create main control keyboard with color and action buttons.
    
    Returns:
        Configured reply keyboard markup
    """
    builder = ReplyKeyboardBuilder()
    
    # Add color buttons
    for emoji in COLORS.keys():
        builder.button(text=emoji)
    
    # Add action buttons
    builder.button(text=EMOJI_RAINBOW)
    builder.button(text=EMOJI_TEMPERATURE)
    
    # Layout: 3 columns for colors, 2 for actions
    builder.adjust(3, 3, 3, 2)
    
    return builder.as_markup(resize_keyboard=True)
