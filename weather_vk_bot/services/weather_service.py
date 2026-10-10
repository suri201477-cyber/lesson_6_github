"""Сервис-посредник между VKBottle и OpenWeatherAPI."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from OpenWeatherAPI import APIConnectionError, CityNotFoundError, OpenWeatherAPI, OpenWeatherAPIError


class WeatherService:
    """Обертка над backend-модулем OpenWeatherAPI для асинхронного бота."""

    def __init__(self, weather_api: OpenWeatherAPI) -> None:
        """Инициализирует сервис.

        Args:
            weather_api: Готовый экземпляр клиента OpenWeather API.
        """
        self.weather_api = weather_api

    async def get_current_by_city(self, city: str, extended: bool = False) -> Dict[str, Any]:
        """Возвращает текущую погоду по городу."""
        return await asyncio.to_thread(
            self.weather_api.get_weather_by_city,
            city,
            extended,
        )

    async def get_forecast_by_city(self, city: str, extended: bool = False) -> Dict[str, Any]:
        """Возвращает прогноз на 5 дней по городу."""
        return await asyncio.to_thread(
            self.weather_api.get_forecast_by_city,
            city,
            extended,
        )

    async def get_current_by_coordinates(
        self, lat: float, lon: float, extended: bool = False
    ) -> Dict[str, Any]:
        """Возвращает текущую погоду по координатам."""
        return await asyncio.to_thread(
            self.weather_api.get_weather_by_coordinates,
            lat,
            lon,
            extended,
        )


__all__ = [
    "WeatherService",
    "OpenWeatherAPIError",
    "CityNotFoundError",
    "APIConnectionError",
]
