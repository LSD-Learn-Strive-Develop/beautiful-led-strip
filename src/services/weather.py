"""Weather service using Yandex Weather API."""

from __future__ import annotations

import math
import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

import requests

if TYPE_CHECKING:
    from src.config import WeatherConfig


class WeatherService:
    """Weather data provider with caching.
    
    Fetches temperature from Yandex Weather API and caches
    results to reduce API calls.
    """
    
    API_URL = "https://api.weather.yandex.ru/graphql/query"
    
    def __init__(self, config: WeatherConfig, cache_file: Path):
        """Initialize weather service.
        
        Args:
            config: Weather configuration with API key and coordinates
            cache_file: Path to cache file for storing weather data
        """
        self.config = config
        self.cache_file = cache_file
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _read_cache(self) -> Optional[Tuple[int, str]]:
        """Read cached weather data.
        
        Returns:
            Tuple of (timestamp, temperature) or None if cache invalid
        """
        try:
            if not self.cache_file.exists():
                return None
            
            lines = self.cache_file.read_text().strip().split("\n")
            if len(lines) >= 2:
                return int(lines[0]), lines[1]
        except (ValueError, OSError):
            pass
        
        return None
    
    def _write_cache(self, temperature: str) -> None:
        """Write weather data to cache.
        
        Args:
            temperature: Temperature value to cache
        """
        timestamp = int(time.time())
        self.cache_file.write_text(f"{timestamp}\n{temperature}")
    
    def _is_cache_valid(self, cached_time: int) -> bool:
        """Check if cached data is still valid.
        
        Args:
            cached_time: Unix timestamp of cached data
            
        Returns:
            True if cache is still valid
        """
        current_time = int(time.time())
        cache_seconds = self.config.cache_minutes * 60
        return current_time - cached_time < cache_seconds
    
    def _fetch_from_api(self) -> Optional[str]:
        """Fetch temperature from Yandex Weather API.
        
        Returns:
            Temperature string or None on error
        """
        try:
            latitude = float(self.config.latitude)
            longitude = float(self.config.longitude)
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError("Weather coordinates are out of range")

            query = (
                "{ weatherByPoint(request: { lat: "
                f"{latitude}, lon: {longitude}"
                " }) { now { temperature } } }"
            )
            headers = {"X-Yandex-Weather-Key": self.config.api_key}
            response = requests.post(
                self.API_URL, headers=headers, json={"query": query}, timeout=10
            )
            response.raise_for_status()

            data = response.json()
            if data.get("errors"):
                raise ValueError("Weather API returned GraphQL errors")
            value = data["data"]["weatherByPoint"]["now"]["temperature"]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("Weather API returned no numeric temperature")
            if not math.isfinite(value):
                raise ValueError("Weather API returned a non-finite temperature")
            temperature = str(round(value))

            self._write_cache(temperature)
            return temperature
            
        except (requests.RequestException, KeyError, TypeError, ValueError, AttributeError) as e:
            print(f"Weather API error: {e}")
            return None
    
    def get_temperature(self) -> Optional[str]:
        """Get current temperature.
        
        Uses cached value if available and valid, otherwise fetches from API.
        
        Returns:
            Temperature string (e.g., "5", "-10") or None on error
        """
        # Try cache first
        cached = self._read_cache()
        
        if cached is not None:
            cached_time, cached_temp = cached
            if self._is_cache_valid(cached_time):
                print("Using cached weather data")
                return cached_temp
        
        # Fetch fresh data
        print("Fetching new weather data")
        return self._fetch_from_api()
    
    def get_temperature_display(self) -> str:
        """Get temperature formatted for 4-digit display.
        
        Formats temperature with degree symbol and Cyrillic С (Celsius).
        Pads to 4 characters if needed.
        
        Returns:
            4-character temperature string (e.g., " 5*C", "-10C")
        """
        temp = self.get_temperature()
        
        if temp is None:
            return "----"
        
        display = f"{temp}*С"
        
        # Pad to 4 characters
        if len(display) < 4:
            display = " " + display
        
        return display[:4]
