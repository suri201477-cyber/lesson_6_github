"""HTTP-слой для запросов к OpenWeather API."""

from __future__ import annotations

from typing import Any, Dict

from requests import Session
from requests.exceptions import RequestException

from .exceptions import APIConnectionError, OpenWeatherAPIError


class OpenWeatherHTTPClient:
    """Базовый HTTP-клиент для безопасного выполнения GET-запросов."""

    def __init__(self, session: Session, api_key: str, timeout: int) -> None:
        """Инициализирует HTTP-клиент.

        Args:
            session: Переиспользуемая HTTP-сессия.
            api_key: Ключ OpenWeatherMap API.
            timeout: Таймаут запроса в секундах.
        """
        self.session = session
        self.api_key = api_key
        self.timeout = timeout

    def make_request(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Выполняет GET-запрос и возвращает JSON-ответ."""
        request_params = dict(params)
        request_params["appid"] = self.api_key

        try:
            response = self.session.get(endpoint, params=request_params, timeout=self.timeout)
            response.raise_for_status()
        except RequestException as exc:
            raise APIConnectionError(f"Ошибка подключения к OpenWeather API: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise OpenWeatherAPIError("OpenWeather API вернул некорректный JSON.") from exc
