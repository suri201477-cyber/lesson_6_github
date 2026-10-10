"""Основной OOP-клиент OpenWeather API для интеграции в production-проект."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from requests import Session

from .air_quality import AirQualityAnalyzer
from .config import OpenWeatherConfig, load_config
from .formatters import WeatherFormatter
from .http_client import OpenWeatherHTTPClient
from .services import AirPollutionService, GeocodingService, WeatherService
from .utils import extract_lat_lon, validate_coordinates


class OpenWeatherAPI:
    """Клиент OpenWeather API со строгим набором endpoint-ов из ТЗ."""

    CURRENT_WEATHER_ENDPOINT = OpenWeatherConfig.current_weather_endpoint
    FORECAST_ENDPOINT = OpenWeatherConfig.forecast_endpoint
    AIR_POLLUTION_ENDPOINT = OpenWeatherConfig.air_pollution_endpoint
    DIRECT_GEOCODE_ENDPOINT = OpenWeatherConfig.direct_geocode_endpoint
    REVERSE_GEOCODE_ENDPOINT = OpenWeatherConfig.reverse_geocode_endpoint

    UV_INDEX_ENDPOINT = OpenWeatherConfig.uv_index_endpoint
    HISTORICAL_ENDPOINT = OpenWeatherConfig.historical_endpoint
    ALERTS_ENDPOINT = OpenWeatherConfig.alerts_endpoint

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 15,
        session: Optional[Session] = None,
    ) -> None:
        """Инициализирует клиент и зависимые сервисы.

        Args:
            api_key: API-ключ OpenWeather. Если не передан, читается из окружения.
            timeout: Таймаут HTTP-запросов в секундах.
            session: Внешняя requests.Session для переиспользования соединений.
        """
        self.config = load_config(api_key=api_key, timeout=timeout)
        self.api_key = self.config.api_key
        self.timeout = self.config.timeout
        self.session = session or requests.Session()

        self._http_client = OpenWeatherHTTPClient(
            session=self.session, api_key=self.api_key, timeout=self.timeout
        )
        self._geocoding_service = GeocodingService(self._http_client, self.config)
        self._weather_service = WeatherService(self._http_client, self.config)
        self._air_service = AirPollutionService(self._http_client, self.config)
        self._air_analyzer = AirQualityAnalyzer()
        self._formatter = WeatherFormatter()

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Внутренний прокси для HTTP-запросов (для совместимости и расширения)."""
        return self._http_client.make_request(endpoint, params)

    def _direct_geocode(self, city: str) -> Dict[str, Any]:
        """Возвращает координаты по названию города."""
        return self._geocoding_service.direct(city)

    def _reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """Возвращает геоданные по координатам."""
        return self._geocoding_service.reverse(lat, lon)

    def _current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Возвращает текущую погоду по координатам."""
        return self._weather_service.current(lat, lon)

    def _forecast_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Возвращает прогноз на 5 дней по координатам."""
        return self._weather_service.forecast(lat, lon)

    def _air_pollution(self, lat: float, lon: float) -> Dict[str, Any]:
        """Возвращает данные загрязнения воздуха по координатам."""
        return self._air_service.current(lat, lon)

    def _analyze_air_quality(self, air_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет бизнес-анализ качества воздуха."""
        return self._air_analyzer.analyze(air_data)

    def _format_basic_weather(
        self, weather_data: Dict[str, Any], air_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Формирует базовый ответ по текущей погоде."""
        return self._formatter.format_basic_weather(weather_data, air_analysis)

    def _format_extended_weather(
        self, weather_data: Dict[str, Any], air_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Формирует расширенный ответ по текущей погоде."""
        return self._formatter.format_extended_weather(weather_data, air_analysis)

    def _format_forecast_data(
        self, forecast_data: Dict[str, Any], air_analysis: Dict[str, Any], extended: bool = False
    ) -> Dict[str, Any]:
        """Формирует ответ по прогнозу погоды."""
        return self._formatter.format_forecast_data(forecast_data, air_analysis, extended=extended)

    def get_weather_by_city(self, city: str, extended: bool = False) -> Dict[str, Any]:
        """Возвращает текущую погоду и качество воздуха по названию города."""
        location = self._direct_geocode(city)
        lat, lon = extract_lat_lon(location)
        return self.get_weather_by_coordinates(lat=lat, lon=lon, extended=extended)

    def get_forecast_by_city(self, city: str, extended: bool = False) -> Dict[str, Any]:
        """Возвращает прогноз на 5 дней и анализ воздуха по названию города."""
        location = self._direct_geocode(city)
        lat, lon = extract_lat_lon(location)

        forecast_data = self._forecast_weather(lat, lon)
        air_data = self._air_pollution(lat, lon)
        air_analysis = self._analyze_air_quality(air_data)
        return self._format_forecast_data(forecast_data, air_analysis, extended=extended)

    def get_weather_by_coordinates(
        self, lat: float, lon: float, extended: bool = False
    ) -> Dict[str, Any]:
        """Возвращает текущую погоду и качество воздуха по координатам."""
        lat, lon = validate_coordinates(lat, lon)
        weather_data = self._current_weather(lat, lon)
        air_data = self._air_pollution(lat, lon)
        air_analysis = self._analyze_air_quality(air_data)
        if extended:
            return self._format_extended_weather(weather_data, air_analysis)
        return self._format_basic_weather(weather_data, air_analysis)

    def close(self) -> None:
        """Закрывает HTTP-сессию клиента."""
        self.session.close()

    def __enter__(self) -> "OpenWeatherAPI":
        """Поддержка контекстного менеджера with."""
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Закрывает сессию при выходе из контекстного менеджера."""
        self.close()
