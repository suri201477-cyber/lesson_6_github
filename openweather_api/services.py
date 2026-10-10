"""Сервисные классы для отдельных групп OpenWeather endpoint-ов."""

from __future__ import annotations

from typing import Any, Dict

from .config import OpenWeatherConfig
from .exceptions import CityNotFoundError
from .http_client import OpenWeatherHTTPClient


class GeocodingService:
    """Сервис работы с прямым и обратным геокодированием."""

    def __init__(self, http_client: OpenWeatherHTTPClient, config: OpenWeatherConfig) -> None:
        """Сохраняет ссылки на HTTP-клиент и конфигурацию endpoint-ов."""
        self.http_client = http_client
        self.config = config

    def direct(self, city: str) -> Dict[str, Any]:
        """Возвращает координаты по названию города."""
        data = self.http_client.make_request(
            self.config.direct_geocode_endpoint,
            {"q": city, "limit": 1},
        )
        if not data:
            raise CityNotFoundError(f"Город '{city}' не найден.")
        return data[0]

    def reverse(self, lat: float, lon: float) -> Dict[str, Any]:
        """Возвращает геоданные по координатам."""
        data = self.http_client.make_request(
            self.config.reverse_geocode_endpoint,
            {"lat": lat, "lon": lon, "limit": 1},
        )
        if not data:
            raise CityNotFoundError(f"Локация по координатам lat={lat}, lon={lon} не найдена.")
        return data[0]


class WeatherService:
    """Сервис запросов текущей погоды и прогноза."""

    def __init__(self, http_client: OpenWeatherHTTPClient, config: OpenWeatherConfig) -> None:
        """Сохраняет ссылки на HTTP-клиент и конфигурацию endpoint-ов."""
        self.http_client = http_client
        self.config = config

    def current(self, lat: float, lon: float) -> Dict[str, Any]:
        """Возвращает текущую погоду по координатам."""
        return self.http_client.make_request(
            self.config.current_weather_endpoint,
            {"lat": lat, "lon": lon},
        )

    def forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Возвращает прогноз на 5 дней по координатам."""
        return self.http_client.make_request(
            self.config.forecast_endpoint,
            {"lat": lat, "lon": lon},
        )


class AirPollutionService:
    """Сервис запросов качества воздуха."""

    def __init__(self, http_client: OpenWeatherHTTPClient, config: OpenWeatherConfig) -> None:
        """Сохраняет ссылки на HTTP-клиент и конфигурацию endpoint-ов."""
        self.http_client = http_client
        self.config = config

    def current(self, lat: float, lon: float) -> Dict[str, Any]:
        """Возвращает данные по загрязнению воздуха по координатам."""
        return self.http_client.make_request(
            self.config.air_pollution_endpoint,
            {"lat": lat, "lon": lon},
        )
