"""Application context and display manager."""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from aiogram import Bot

if TYPE_CHECKING:
    from src.config import Config
    from src.led.controller import LEDController


class DisplayMode(Enum):
    """Operating modes for the display."""
    MAIN = auto()      # Normal: weather + time cycle
    USER = auto()      # User mode with custom messages
    FIGHT = auto()     # Countdown mode (normal speed)
    FIGHT_FAST = auto()  # Countdown mode (fast updates in final minute)


class ColorStorage:
    """Persistent color storage using file."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_dir()
    
    def _ensure_dir(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_color(self) -> tuple[int, int, int]:
        """Load color from file.
        
        Returns:
            RGB tuple, defaults to (0, 0, 0) if file doesn't exist
        """
        try:
            if self.file_path.exists():
                parts = self.file_path.read_text().strip().split()
                if len(parts) >= 3:
                    return (int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, OSError):
            pass
        
        return (0, 0, 0)
    
    def save_color(self, rgb: tuple[int, int, int]) -> None:
        """Save color to file.
        
        Args:
            rgb: RGB color tuple
        """
        self.file_path.write_text(f"{rgb[0]} {rgb[1]} {rgb[2]}")


class DisplayManager:
    """Manages display state and content updates."""
    
    def __init__(
        self,
        led_controller: LEDController,
        config: Config,
    ):
        self.led = led_controller
        self.config = config
        self._mode = DisplayMode.MAIN
        self._pending_action: Optional[str] = None
        self._pending_text: Optional[str] = None
        self._pending_slots: Optional[int] = None  # Dice value for slot machine
        self._slots_active: bool = False  # True while slots animation is running
        self._rainbow_mode: bool = False
        self._new_year_date: datetime = config.new_year_date
    
    @property
    def mode(self) -> DisplayMode:
        return self._mode
    
    def set_mode(self, mode_str: str) -> None:
        """Set display mode from string.
        
        Args:
            mode_str: One of 'main', 'user', 'fight'
        """
        mode_map = {
            "main": DisplayMode.MAIN,
            "user": DisplayMode.USER,
            "fight": DisplayMode.FIGHT,
        }
        self._mode = mode_map.get(mode_str, DisplayMode.MAIN)
    
    def request_refresh(self) -> None:
        """Request a display refresh (e.g., after color change)."""
        self._pending_action = "refresh"
    
    def show_rainbow(self) -> None:
        """Toggle rainbow color mode."""
        self._rainbow_mode = not self._rainbow_mode
        self._pending_action = "refresh"
    
    @property
    def rainbow_mode(self) -> bool:
        """Check if rainbow mode is active."""
        return self._rainbow_mode
    
    def enable_rainbow(self) -> None:
        """Enable rainbow color mode."""
        self._rainbow_mode = True
    
    def disable_rainbow(self) -> None:
        """Disable rainbow mode (when user sets a color)."""
        self._rainbow_mode = False
    
    def show_temperature(self) -> None:
        """Request temperature display."""
        self._pending_action = "temperature"
    
    def show_text(self, text: str) -> None:
        """Request text display.
        
        Args:
            text: Text to display
        """
        self._pending_text = text
    
    def show_slots(self, dice_value: int) -> bool:
        """Request slot machine display.
        
        Takes priority over other display modes.
        Ignores request if slots animation is already running.
        
        Args:
            dice_value: Telegram dice value (1-64)
            
        Returns:
            True if request accepted, False if slots already active
        """
        if self._slots_active:
            return False
        self._pending_slots = dice_value
        return True
    
    @property
    def slots_active(self) -> bool:
        """Check if slots animation is currently running."""
        return self._slots_active
    
    def set_slots_active(self, active: bool) -> None:
        """Set slots animation state.
        
        Args:
            active: True when animation starts, False when it ends
        """
        self._slots_active = active
    
    def get_pending_action(self) -> Optional[str]:
        """Get and clear pending action.
        
        Returns:
            Pending action string or None
        """
        action = self._pending_action
        self._pending_action = None
        return action
    
    def get_pending_text(self) -> Optional[str]:
        """Get and clear pending text.
        
        Returns:
            Pending text string or None
        """
        text = self._pending_text
        self._pending_text = None
        return text
    
    def get_pending_slots(self) -> Optional[int]:
        """Get and clear pending slot machine dice value.
        
        Returns:
            Pending dice value (1-64) or None
        """
        slots = self._pending_slots
        self._pending_slots = None
        return slots
    
    def enter_fast_mode(self) -> None:
        """Switch to fast countdown mode (final minute)."""
        if self._mode == DisplayMode.FIGHT:
            self._mode = DisplayMode.FIGHT_FAST
    
    def exit_countdown(self) -> None:
        """Exit countdown mode after completion."""
        self._mode = DisplayMode.MAIN
    
    def is_countdown_protected(self) -> bool:
        """Check if countdown is in protected mode (final minute or fast mode).
        
        During protected mode, only admins can interact with the display.
        
        Returns:
            True if in FIGHT_FAST mode (last minute before New Year)
        """
        return self._mode == DisplayMode.FIGHT_FAST
    
    def get_random_color_from_existing(self) -> tuple[int, int, int]:
        """Get a random color from existing colors (excluding black).
        
        Returns:
            Random RGB tuple from existing colors
        """
        from src.led.symbols import RGB_COLORS
        
        # Get all colors except black
        available_colors = [
            rgb for name, rgb in RGB_COLORS.items() if name != "Черный"
        ]
        
        return random.choice(available_colors)
    
    @property
    def new_year_date(self) -> datetime:
        """Get current New Year date."""
        return self._new_year_date
    
    def set_new_year_date(self, date: datetime) -> None:
        """Set New Year date.
        
        Args:
            date: New target datetime
        """
        self._new_year_date = date


@dataclass
class AppContext:
    """Application context shared across handlers."""
    config: Config
    bot: Bot
    led_controller: LEDController
    color_storage: ColorStorage
    display_manager: DisplayManager
    admin_manager: "AdminManager"


# Import at bottom to avoid circular imports
from src.bot.admin_manager import AdminManager
