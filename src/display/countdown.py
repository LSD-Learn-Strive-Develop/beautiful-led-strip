"""Countdown display for New Year countdown."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.led.controller import LEDController


class CountdownDisplay:
    """Display countdown to a target date.
    
    Shows remaining time in the most significant unit:
    - Hours if > 1 hour remaining
    - Minutes if > 1 minute remaining  
    - Seconds otherwise
    """
    
    def __init__(self, led_controller: LEDController, target_date: datetime):
        """Initialize countdown display.
        
        Args:
            led_controller: LED controller instance
            target_date: Target datetime to count down to
        """
        self.led = led_controller
        self.target_date = target_date
        self._last_value: str = ""
    
    def set_target_date(self, target_date: datetime) -> None:
        """Update target date for countdown.
        
        Args:
            target_date: New target datetime
        """
        self.target_date = target_date
        self._last_value = ""  # Reset last value to force update
    
    @property
    def last_displayed_value(self) -> str:
        """Get the last displayed countdown value."""
        return self._last_value
    
    def get_countdown_string(self) -> str:
        """Calculate countdown and format as 4-digit string.
        
        Returns:
            4-digit string with leading zeros, or empty if countdown complete
        """
        now = datetime.now()
        delta = self.target_date - now
        
        if delta.total_seconds() <= 0:
            return ""
        
        total_seconds = int(delta.total_seconds())
        minutes = total_seconds // 60
        hours = minutes // 60
        seconds = total_seconds % 60
        minutes = minutes % 60
        
        # Show most significant unit
        if hours > 0:
            value = hours
        elif minutes > 0:
            value = minutes
        else:
            value = seconds
        
        # Pad to 4 digits
        return str(value).zfill(4)
    
    def is_complete(self) -> bool:
        """Check if countdown has reached zero.
        
        Returns:
            True if target date has passed
        """
        return datetime.now() >= self.target_date
    
    def is_final_minute(self) -> bool:
        """Check if in final minute of countdown.
        
        Returns:
            True if less than 60 seconds remaining
        """
        delta = self.target_date - datetime.now()
        return 0 < delta.total_seconds() < 60
    
    def value_changed(self) -> bool:
        """Check if countdown value differs from last displayed.
        
        Returns:
            True if value has changed
        """
        return self.get_countdown_string() != self._last_value
    
    async def show_countdown(self, fast: bool = False) -> str:
        """Display current countdown value.
        
        Args:
            fast: If True, don't animate segments
            
        Returns:
            Countdown string that was displayed
        """
        countdown_str = self.get_countdown_string()
        
        if not countdown_str:
            return ""
        
        for i, digit in enumerate(countdown_str):
            await self.led.show_symbol(i, int(digit), fast)
        
        self._last_value = countdown_str
        return countdown_str
