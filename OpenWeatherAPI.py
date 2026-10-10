"""Совместимый фасад для импорта production-клиента OpenWeather API."""

from openweather_api import (
    APIConnectionError,
    CityNotFoundError,
    OpenWeatherAPI,
    OpenWeatherAPIError,
)

__all__ = ["OpenWeatherAPI", "OpenWeatherAPIError", "CityNotFoundError", "APIConnectionError"]
