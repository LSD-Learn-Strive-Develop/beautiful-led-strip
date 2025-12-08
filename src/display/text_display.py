"""Text display functionality."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.led.controller import LEDController


class TextDisplay:
    """Display scrolling or static text on LED strip."""
    
    def __init__(self, led_controller: LEDController):
        """Initialize text display.
        
        Args:
            led_controller: LED controller instance
        """
        self.led = led_controller
    
    async def show_scrolling_text(
        self,
        text: str,
        scroll_delay: float = 0.7,
    ) -> None:
        """Display scrolling text.
        
        Text is padded with spaces and scrolls left to right.
        
        Args:
            text: Text to display
            scroll_delay: Delay between scroll steps in seconds
        """
        await self.led.show_text(text, scroll_delay)
    
    async def show_static_text(self, text: str, fast: bool = True) -> None:
        """Display static 4-character text.
        
        If text is shorter than 4 characters, it's left-padded with spaces.
        If longer, it's truncated to 4 characters.
        
        Args:
            text: Text to display (max 4 characters shown)
            fast: If True, don't animate segments
        """
        # Pad or truncate to 4 characters
        display_text = text[:4].rjust(4)
        await self.led.show_digits(display_text, fast)
