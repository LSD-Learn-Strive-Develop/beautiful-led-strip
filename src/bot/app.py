"""Application context and display manager."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
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
        self._rainbow_mode: bool = False
    
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
    
    def enter_fast_mode(self) -> None:
        """Switch to fast countdown mode (final minute)."""
        if self._mode == DisplayMode.FIGHT:
            self._mode = DisplayMode.FIGHT_FAST
    
    def exit_countdown(self) -> None:
        """Exit countdown mode after completion."""
        self._mode = DisplayMode.USER


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
