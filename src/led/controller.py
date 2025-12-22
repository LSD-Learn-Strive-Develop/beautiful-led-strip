"""LED Strip controller for NeoPixel hardware.

Provides high-level interface for controlling LED strip display.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Tuple

from .symbols import get_symbol_definition, get_slot_symbol_definition, SymbolDef, RGB_COLORS

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
        self.rainbow_mode: bool = False
        self._rainbow_offset: int = 0  # For animation
        self._lit_pixels: set = set()  # Track which pixels are currently lit
    
    def set_color(self, rgb: tuple[int, int, int]) -> None:
        """Set the current display color.
        
        Args:
            rgb: Color as (red, green, blue) tuple, values 0-255
        """
        self.current_color = rgb
    
    def _get_rainbow_color(self, pixel_index: int) -> Tuple[int, int, int]:
        """Get rainbow color for a specific pixel.
        
        Args:
            pixel_index: Index of the pixel in the strip
            
        Returns:
            RGB color tuple
        """
        # Use time-based offset for subtle animation
        offset = int(time.time() * 50) % 256
        position = (int(pixel_index * 256 / self.config.count) + offset) & 255
        
        if position < 85:
            return (position * 3, 255 - position * 3, 0)
        elif position < 170:
            position -= 85
            return (255 - position * 3, 0, position * 3)
        else:
            position -= 170
            return (0, position * 3, 255 - position * 3)
    
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
            self._lit_pixels.discard(i)  # Remove from lit set
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
        override_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a single segment block.
        
        Args:
            offset: Starting pixel offset for the symbol position
            block: Block definition [segment, direction, start?, end?]
            fast: If True, don't show updates between pixels
            override_color: Optional color to use instead of current_color
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
            pixel_index = segment_offset + j
            if override_color:
                color = override_color
            elif self.rainbow_mode:
                color = self._get_rainbow_color(pixel_index)
            else:
                color = self.current_color
            self.pixels[pixel_index] = color
            self._lit_pixels.add(pixel_index)  # Track this pixel as lit
            if not fast:
                self.pixels.show()
    
    async def show_slot_symbol(
        self,
        position: int,
        slot_name: str,
        fast: bool = False,
    ) -> None:
        """Display a slot machine symbol at the specified position.
        
        Each slot symbol has its own colors defined in SLOT_SYMBOLS.
        
        Args:
            position: Display position (0-3, where 0 is rightmost)
            slot_name: Slot symbol name ('bar', 'grapes', 'lemon', 'seven')
            fast: If True, update display at once; otherwise animate
        """
        colored_blocks = get_slot_symbol_definition(slot_name)
        if colored_blocks is None:
            print(f"Unknown slot symbol: {slot_name}")
            return
        
        offset = self._get_symbol_offset(position)
        
        # Clear the position first
        for i in range(offset, offset + self.config.pixels_per_symbol):
            self.pixels[i] = (0, 0, 0)
            self._lit_pixels.discard(i)
        self.pixels.show()
        
        # Draw each colored block
        for colored_block in colored_blocks:
            # Parse colored block: (segment, direction, color) or (segment, direction, start, end, color)
            if len(colored_block) == 3:
                segment, direction, color_name = colored_block
                block = [segment, direction]
            else:
                segment, direction, start, end, color_name = colored_block
                block = [segment, direction, start, end]
            
            # Get RGB color from color name
            rgb_color = RGB_COLORS.get(color_name, (255, 255, 255))
            
            await self._draw_block(offset, block, fast, override_color=rgb_color)
        
        if fast:
            self.pixels.show()
    
    def clear_position(self, position: int) -> None:
        """Clear a single display position.
        
        Args:
            position: Display position to clear (0-3)
        """
        offset = self._get_symbol_offset(position)
        for i in range(offset, offset + self.config.pixels_per_symbol):
            self.pixels[i] = (0, 0, 0)
            self._lit_pixels.discard(i)
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
    
    def update_colors(self) -> None:
        """Update colors of all currently lit pixels without redrawing structure.
        
        Used for smooth rainbow animation without flickering.
        Only updates pixels tracked in _lit_pixels set.
        """
        for pixel_index in self._lit_pixels:
            if self.rainbow_mode:
                self.pixels[pixel_index] = self._get_rainbow_color(pixel_index)
            else:
                self.pixels[pixel_index] = self.current_color
        
        self.pixels.show()



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
