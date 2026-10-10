"""Пакет OpenWeather API для модульной интеграции в погодного бота."""

from .client import OpenWeatherAPI
from .config import OpenWeatherConfig, load_config
from .exceptions import APIConnectionError, CityNotFoundError, OpenWeatherAPIError

__all__ = [
    "OpenWeatherAPI",
    "OpenWeatherConfig",
    "load_config",
    "OpenWeatherAPIError",
    "CityNotFoundError",
    "APIConnectionError",
]
