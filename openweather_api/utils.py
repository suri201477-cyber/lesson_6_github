"""Вспомогательные функции для валидации и сериализации данных."""

from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from .exceptions import OpenWeatherAPIError


def validate_coordinates(lat: float, lon: float) -> Tuple[float, float]:
    """Проверяет диапазоны координат и возвращает нормализованные значения."""
    lat_value = float(lat)
    lon_value = float(lon)
    if not -90.0 <= lat_value <= 90.0:
        raise OpenWeatherAPIError("Широта должна быть в диапазоне от -90 до 90.")
    if not -180.0 <= lon_value <= 180.0:
        raise OpenWeatherAPIError("Долгота должна быть в диапазоне от -180 до 180.")
    return lat_value, lon_value


def extract_lat_lon(location_data: Dict[str, Any]) -> Tuple[float, float]:
    """Извлекает широту и долготу из ответа геокодирования."""
    lat = location_data.get("lat")
    lon = location_data.get("lon")
    if lat is None or lon is None:
        raise OpenWeatherAPIError("Geo API вернул неполные координаты для указанной локации.")
    return float(lat), float(lon)


def to_pretty_json(data: Dict[str, Any]) -> str:
    """Возвращает JSON-строку с отступами и поддержкой русских символов."""
    return json.dumps(data, ensure_ascii=False, indent=2)
