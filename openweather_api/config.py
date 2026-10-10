"""Конфигурация клиента OpenWeather API и системные константы."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

from .exceptions import OpenWeatherAPIError


@dataclass(frozen=True)
class OpenWeatherConfig:
    """Конфигурация и endpoint-адреса OpenWeather API."""

    api_key: str
    timeout: int = 15

    current_weather_endpoint: str = "https://api.openweathermap.org/data/2.5/weather"
    forecast_endpoint: str = "https://api.openweathermap.org/data/2.5/forecast"
    air_pollution_endpoint: str = "http://api.openweathermap.org/data/2.5/air_pollution"
    direct_geocode_endpoint: str = "http://api.openweathermap.org/geo/1.0/direct"
    reverse_geocode_endpoint: str = "http://api.openweathermap.org/geo/1.0/reverse"

    # Резерв для масштабирования.
    uv_index_endpoint: Optional[str] = None
    historical_endpoint: Optional[str] = None
    alerts_endpoint: Optional[str] = None


def load_config(api_key: Optional[str] = None, timeout: int = 15) -> OpenWeatherConfig:
    """Собирает конфигурацию из аргументов и переменных окружения."""
    load_dotenv()
    resolved_api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not resolved_api_key:
        raise OpenWeatherAPIError(
            "API-ключ OpenWeather не найден. Передайте api_key или задайте OPENWEATHER_API_KEY."
        )
    return OpenWeatherConfig(api_key=resolved_api_key, timeout=timeout)
