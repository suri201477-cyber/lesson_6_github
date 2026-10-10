"""Пользовательские исключения для клиента OpenWeather API."""


class OpenWeatherAPIError(Exception):
    """Базовое исключение для ошибок OpenWeather API."""


class CityNotFoundError(OpenWeatherAPIError):
    """Исключение для ситуации, когда геокодирование не находит город."""


class APIConnectionError(OpenWeatherAPIError):
    """Исключение для сетевых ошибок и недоступности API."""
