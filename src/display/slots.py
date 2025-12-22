"""Slot machine display for LED strip.

Displays Telegram slot machine results on the first 3 digit positions.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from src.led.symbols import get_slot_combo_parts, is_slot_jackpot

if TYPE_CHECKING:
    from src.led.controller import LEDController


class SlotsDisplay:
    """Display slot machine results on LED strip.
    
    Shows three slot symbols sequentially from left to right,
    simulating the Telegram slot machine animation timing.
    
    The display uses positions 0-2 (leftmost three digits),
    leaving position 3 empty.
    """
    
    # Timing constants (Telegram animation is ~3 seconds total)
    REEL_DELAY = 0.3  # Seconds between each reel stop
    TOTAL_DURATION = 3.0  # Total animation time
    
    # Jackpot celebration
    JACKPOT_BLINK_COUNT = 3  # Number of blinks for jackpot
    JACKPOT_BLINK_DELAY = 0.5  # Seconds between blinks
    
    # Position mapping: slot index -> LED position
    # Slots go left to right (0, 1, 2), LED positions are (0, 1, 2) from left
    SLOT_POSITIONS = [0, 1, 2]
    
    def __init__(self, led_controller: LEDController):
        """Initialize slots display.
        
        Args:
            led_controller: LED controller instance
        """
        self.led = led_controller
        self._is_active = False
    
    @property
    def is_active(self) -> bool:
        """Check if slot animation is currently running."""
        return self._is_active
    
    async def show_slots(self, dice_value: int, fast: bool = False) -> bool:
        """Display slot machine result.
        
        Shows three slot symbols one by one from left to right,
        with 1-second delay between each to match Telegram animation.
        
        Args:
            dice_value: Telegram dice value (1-64)
            fast: If True, skip animation delays
            
        Returns:
            True if it's a jackpot (all three match)
        """
        self._is_active = True
        
        try:
            # Get slot symbols from dice value
            symbols = get_slot_combo_parts(dice_value)
            
            # Clear all positions first
            for pos in self.SLOT_POSITIONS:
                self.led.clear_position(pos)
            # Also clear position 3 (rightmost)
            self.led.clear_position(3)
            
            # Display each slot symbol with delay
            for i, (symbol, position) in enumerate(zip(symbols, self.SLOT_POSITIONS)):
                await self.led.show_slot_symbol(position, symbol, fast=fast)
                
                # Wait between reels (except after the last one)
                if not fast and i < len(symbols) - 1:
                    await asyncio.sleep(self.REEL_DELAY)
            
            # Check for jackpot and celebrate!
            jackpot = is_slot_jackpot(dice_value)
            if jackpot:
                await self._celebrate_jackpot(symbols)
            
            return jackpot
            
        finally:
            self._is_active = False
    
    async def _celebrate_jackpot(self, symbols: list[str]) -> None:
        """Blink slots 3 times to celebrate jackpot.
        
        Args:
            symbols: List of slot symbols to blink
        """
        for _ in range(self.JACKPOT_BLINK_COUNT):
            # Turn off
            for pos in self.SLOT_POSITIONS:
                self.led.clear_position(pos)
            await asyncio.sleep(self.JACKPOT_BLINK_DELAY)
            
            # Turn on (fast, no animation)
            for symbol, position in zip(symbols, self.SLOT_POSITIONS):
                await self.led.show_slot_symbol(position, symbol, fast=True)
            await asyncio.sleep(self.JACKPOT_BLINK_DELAY)
    
    async def clear_slots(self) -> None:
        """Clear slot display positions."""
        for pos in self.SLOT_POSITIONS:
            self.led.clear_position(pos)
        self.led.clear_position(3)
