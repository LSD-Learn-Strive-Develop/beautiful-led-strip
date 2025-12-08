"""LED visual effects like rainbow animation."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .controller import LEDController


async def wheel(position: int) -> tuple[int, int, int]:
    """Generate rainbow color from wheel position.
    
    Creates smooth color transitions through the spectrum.
    
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


async def rainbow_cycle(controller: LEDController, wait: float = 0.002) -> None:
    """Display rainbow color cycle across entire LED strip.
    
    Creates a smooth rainbow animation that cycles through all colors.
    
    Args:
        controller: LED controller instance
        wait: Delay between frames (currently unused for speed)
    """
    pixel_count = controller.config.count
    
    for j in range(256):
        for i in range(pixel_count):
            color_position = (int(i * 256 / pixel_count) + j) & 255
            controller.pixels[i] = await wheel(color_position)
        
        controller.pixels.show()
        # Uncomment for slower animation:
        # await asyncio.sleep(wait)
