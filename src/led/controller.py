"""LED Strip controller for NeoPixel hardware.

Provides high-level interface for controlling LED strip display.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from .symbols import get_symbol_definition, SymbolDef

if TYPE_CHECKING:
    from src.config import LEDConfig


class LEDController:
    """Controller for NeoPixel LED strip display.
    
    Manages a 4-digit display where each digit position uses 98 pixels
    arranged in 7 segments of 14 LEDs each.
    
    Attributes:
        pixels: NeoPixel strip object
        config: LED configuration
        current_color: Current display color as RGB tuple
    """
    
    SYMBOL_POSITIONS = 4  # Number of digit positions
    
    def __init__(self, config: LEDConfig):
        """Initialize LED controller.
        
        Args:
            config: LED configuration with pin and count settings
        """
        import board
        import neopixel
        
        self.config = config
        
        # Get pin from board module dynamically
        pin = getattr(board, config.pin)
        self.pixels = neopixel.NeoPixel(
            pin,
            config.count,
            auto_write=False,
        )
        
        self.current_color: tuple[int, int, int] = (0, 0, 0)
    
    def set_color(self, rgb: tuple[int, int, int]) -> None:
        """Set the current display color.
        
        Args:
            rgb: Color as (red, green, blue) tuple, values 0-255
        """
        self.current_color = rgb
    
    def clear(self) -> None:
        """Turn off all pixels."""
        for i in range(self.config.count):
            self.pixels[i] = (0, 0, 0)
        self.pixels.show()
    
    def _get_symbol_offset(self, position: int) -> int:
        """Calculate pixel offset for a symbol position.
        
        Position 0 is rightmost, position 3 is leftmost.
        
        Args:
            position: Symbol position (0-3)
            
        Returns:
            Starting pixel index for the position
        """
        return self.config.pixels_per_symbol * (self.SYMBOL_POSITIONS - 1 - position)
    
    async def show_symbol(
        self,
        position: int,
        symbol: str | int,
        fast: bool = False,
    ) -> None:
        """Display a symbol at the specified position.
        
        Args:
            position: Display position (0-3, where 0 is rightmost)
            symbol: Character or digit to display
            fast: If True, update display at once; otherwise animate
        """
        blocks = get_symbol_definition(symbol)
        if blocks is None:
            print(f"Unknown symbol: {symbol}")
            return
        
        offset = self._get_symbol_offset(position)
        
        # Clear the position first
        for i in range(offset, offset + self.config.pixels_per_symbol):
            self.pixels[i] = (0, 0, 0)
        self.pixels.show()
        
        # Draw each block (segment)
        for block in blocks:
            await self._draw_block(offset, block, fast)
        
        if fast:
            self.pixels.show()
    
    async def _draw_block(
        self,
        offset: int,
        block: list[int],
        fast: bool,
    ) -> None:
        """Draw a single segment block.
        
        Args:
            offset: Starting pixel offset for the symbol position
            block: Block definition [segment, direction, start?, end?]
            fast: If True, don't show updates between pixels
        """
        segment = block[0]
        direction = block[1]
        
        # Determine LED range within segment
        if len(block) == 2:
            # Full segment
            start, end = 0, self.config.leds_per_segment
        else:
            start, end = block[2], block[3]
        
        # Calculate step direction
        if direction == 1:  # Backward
            start, end = end - 1, start - 1
            step = -1
        else:  # Forward
            step = 1
        
        # Light up LEDs in segment
        segment_offset = offset + self.config.leds_per_segment * (segment - 1)
        
        for j in range(start, end, step):
            self.pixels[segment_offset + j] = self.current_color
            if not fast:
                self.pixels.show()
    
    async def show_text(self, text: str, scroll_delay: float = 0.7) -> None:
        """Display scrolling text.
        
        Args:
            text: Text to display (will be padded and scrolled)
            scroll_delay: Delay between scroll steps in seconds
        """
        padded = "    " + text + "    "
        
        for i in range(len(padded) - 3):
            window = padded[i:i + 4]
            
            for pos, char in enumerate(window):
                try:
                    symbol = int(char)
                except ValueError:
                    symbol = char
                
                await self.show_symbol(pos, symbol, fast=True)
            
            await asyncio.sleep(scroll_delay)
    
    async def show_digits(self, digits: str, fast: bool = False) -> None:
        """Display 4 digits/characters.
        
        Args:
            digits: String of exactly 4 characters to display
            fast: If True, don't animate individual segments
        """
        for i, char in enumerate(digits[:4]):
            try:
                symbol = int(char)
            except ValueError:
                symbol = char
            
            await self.show_symbol(i, symbol, fast)


async def wheel(position: int) -> tuple[int, int, int]:
    """Generate rainbow color from wheel position.
    
    Args:
        position: Wheel position (0-255)
        
    Returns:
        RGB color tuple
    """
    if position < 85:
        return (position * 3, 255 - position * 3, 0)
    elif position < 170:
        position -= 85
        return (255 - position * 3, 0, position * 3)
    else:
        position -= 170
        return (0, position * 3, 255 - position * 3)
