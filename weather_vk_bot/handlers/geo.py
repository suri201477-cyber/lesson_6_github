"""Сценарий погоды по геолокации и координатам."""

from __future__ import annotations

import logging
import re
from typing import Optional, Tuple

from vkbottle.bot import Bot, Message

from weather_vk_bot.keyboards.main_keyboard import get_main_keyboard
from weather_vk_bot.keyboards.navigation_keyboard import get_navigation_keyboard
from weather_vk_bot.services.formatter import WeatherFormatter
from weather_vk_bot.services.state_manager import StateManager, WeatherStates
from weather_vk_bot.services.weather_service import APIConnectionError, OpenWeatherAPIError, WeatherService


logger = logging.getLogger(__name__)

_COORDS_PATTERN = re.compile(
    r"^\s*([+-]?\d+(?:\.\d+)?)\s*[, ]\s*([+-]?\d+(?:\.\d+)?)\s*$"
)


def _parse_coordinates(text: str) -> Optional[Tuple[float, float]]:
    """Парсит координаты формата '55.7558,37.6173' или '55.7558 37.6173'."""
    match = _COORDS_PATTERN.match(text)
    if not match:
        return None
    return float(match.group(1)), float(match.group(2))


def _extract_geo(message: Message) -> Optional[Tuple[float, float]]:
    """Пытается извлечь координаты из geo-вложения VK сообщения."""
    geo = getattr(message, "geo", None)
    if not geo:
        return None

    coordinates = getattr(geo, "coordinates", None)
    if not coordinates:
        return None

    lat = getattr(coordinates, "latitude", None)
    lon = getattr(coordinates, "longitude", None)
    if lat is None or lon is None:
        return None
    return float(lat), float(lon)


def register_geo_handlers(
    bot: Bot,
    weather_service: WeatherService,
    formatter: WeatherFormatter,
    state_manager: StateManager,
) -> None:
    """Регистрирует хендлеры для геолокации и координат."""

    @bot.on.message(text="📍 Геолокация")
    async def request_geo(message: Message) -> None:
        """Запрашивает у пользователя геопозицию или координаты."""
        await state_manager.set_state(message.from_id, WeatherStates.WAITING_GEO)
        await message.answer(
            "Отправьте геолокацию VK или координаты в формате: 55.7558, 37.6173",
            keyboard=get_navigation_keyboard(),
        )

    @bot.on.message(state=WeatherStates.WAITING_GEO)
    async def handle_geo(message: Message) -> None:
        """Обрабатывает геолокацию или координаты и возвращает текущую погоду."""
        parsed = _extract_geo(message)
        if parsed is None:
            parsed = _parse_coordinates((message.text or "").strip())

        if parsed is None:
            await message.answer(
                formatter.format_error(
                    "Ошибка геолокации. Отправьте координаты в формате: 55.7558, 37.6173"
                )
            )
            return

        lat, lon = parsed
        try:
            result = await weather_service.get_current_by_coordinates(lat=lat, lon=lon)
            await message.answer(formatter.format_current(result, extended=False))
            await state_manager.set_state(message.from_id, WeatherStates.MAIN_MENU)
            await message.answer("Главное меню:", keyboard=get_main_keyboard())
        except APIConnectionError:
            await message.answer(formatter.format_error("Сервис погоды временно недоступен."))
        except OpenWeatherAPIError as exc:
            logger.exception("Ошибка при обработке геолокации")
            await message.answer(formatter.format_error(str(exc)))
