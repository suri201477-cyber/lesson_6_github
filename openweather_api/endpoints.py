"""Константы endpoint-адресов OpenWeatherMap API."""

from typing import Optional


CURRENT_WEATHER_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"
AIR_POLLUTION_ENDPOINT = "http://api.openweathermap.org/data/2.5/air_pollution"
DIRECT_GEOCODE_ENDPOINT = "http://api.openweathermap.org/geo/1.0/direct"
REVERSE_GEOCODE_ENDPOINT = "http://api.openweathermap.org/geo/1.0/reverse"

# Резерв для масштабирования.
UV_INDEX_ENDPOINT: Optional[str] = None
HISTORICAL_ENDPOINT: Optional[str] = None
ALERTS_ENDPOINT: Optional[str] = None
