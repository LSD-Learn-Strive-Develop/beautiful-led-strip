"""Time display functionality."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.led.controller import LEDController


class TimeDisplay:
    """Display current time on LED strip.
    
    Shows time in HHMM format on 4-digit display.
    """
    
    def __init__(self, led_controller: LEDController):
        """Initialize time display.
        
        Args:
            led_controller: LED controller instance
        """
        self.led = led_controller
        self._last_time: str = ""
    
    @property
    def last_displayed_time(self) -> str:
        """Get the last displayed time string."""
        return self._last_time
    
    async def show_current_time(self, fast: bool = False) -> str:
        """Display current time.
        
        Args:
            fast: If True, don't animate segments
            
        Returns:
            Time string that was displayed (HHMM format)
        """
        time_str = datetime.now().strftime("%H%M")
        
        for i, digit in enumerate(time_str):
            await self.led.show_symbol(i, int(digit), fast)
        
        self._last_time = time_str
        return time_str
    
    async def show_year(self, fast: bool = False) -> str:
        """Display current year.
        
        Args:
            fast: If True, don't animate segments
            
        Returns:
            Year string that was displayed
        """
        year_str = datetime.now().strftime("%Y")
        
        for i, digit in enumerate(year_str):
            await self.led.show_symbol(i, int(digit), fast)
        
        return year_str
    
    def time_changed(self) -> bool:
        """Check if current time differs from last displayed.
        
        Returns:
            True if time has changed
        """
        current = datetime.now().strftime("%H%M")
        return current != self._last_time
