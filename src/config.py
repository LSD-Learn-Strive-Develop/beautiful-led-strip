"""Configuration management for LED Strip project.

Loads settings from environment variables (.env file).
"""

import os
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


def _get_env(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """Get environment variable with optional default and required check."""
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable {key} is not set")
    return value or ""


@dataclass(frozen=True)
class TelegramConfig:
    """Telegram bot configuration."""
    bot_token: str
    admin_id: int


@dataclass(frozen=True)
class WeatherConfig:
    """Yandex Weather API configuration."""
    api_key: str
    latitude: str
    longitude: str
    cache_minutes: int = 30


@dataclass(frozen=True)
class LEDConfig:
    """LED strip hardware configuration."""
    pin: str
    count: int
    pixels_per_symbol: int = 98
    segments_per_symbol: int = 7
    leds_per_segment: int = 14


@dataclass(frozen=True)
class Config:
    """Main application configuration."""
    telegram: TelegramConfig
    weather: WeatherConfig
    led: LEDConfig
    new_year_date: datetime
    base_dir: Path
    data_dir: Path


def load_config() -> Config:
    """Load configuration from environment variables.
    
    Returns:
        Config: Application configuration object
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not installed, rely on system env vars
    
    base_dir = Path(__file__).parent.parent
    
    return Config(
        telegram=TelegramConfig(
            bot_token=_get_env("TELEGRAM_BOT_TOKEN", required=True),
            admin_id=int(_get_env("TELEGRAM_ADMIN_ID", "0")),
        ),
        weather=WeatherConfig(
            api_key=_get_env("YANDEX_WEATHER_API_KEY", required=True),
            latitude=_get_env("YANDEX_WEATHER_LAT", "59.873546"),
            longitude=_get_env("YANDEX_WEATHER_LON", "29.827624"),
            cache_minutes=int(_get_env("WEATHER_CACHE_MINUTES", "30")),
        ),
        led=LEDConfig(
            pin=_get_env("LED_PIN", "D18"),
            count=int(_get_env("LED_COUNT", "392")),
        ),
        new_year_date=datetime.strptime(
            _get_env("NEW_YEAR_DATE", "2026-01-01 00:00:00"),
            "%Y-%m-%d %H:%M:%S"
        ),
        base_dir=base_dir,
        data_dir=base_dir / "data",
    )


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance.
    
    Returns:
        Config: Application configuration object
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config
