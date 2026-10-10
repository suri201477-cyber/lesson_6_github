"""Сценарий прогноза на 5 дней по городу."""

from __future__ import annotations

import logging

from vkbottle.bot import Bot, Message

from weather_vk_bot.keyboards.main_keyboard import get_main_keyboard
from weather_vk_bot.keyboards.navigation_keyboard import get_navigation_keyboard
from weather_vk_bot.services.formatter import WeatherFormatter
from weather_vk_bot.services.state_manager import StateManager, WeatherStates
from weather_vk_bot.services.weather_service import (
    APIConnectionError,
    CityNotFoundError,
    OpenWeatherAPIError,
    WeatherService,
)


logger = logging.getLogger(__name__)


def register_forecast_handlers(
    bot: Bot,
    weather_service: WeatherService,
    formatter: WeatherFormatter,
    state_manager: StateManager,
) -> None:
    """Регистрирует хендлеры для 5-дневного прогноза."""

    @bot.on.message(text="📅 Прогноз 5 дней")
    async def request_city_for_forecast(message: Message) -> None:
        """Переводит пользователя в состояние ожидания города для прогноза."""
        await state_manager.set_state(message.from_id, WeatherStates.WAITING_FORECAST_CITY)
        await message.answer(
            "Введите город для прогноза на 5 дней:",
            keyboard=get_navigation_keyboard(),
        )

    @bot.on.message(state=WeatherStates.WAITING_FORECAST_CITY)
    async def handle_city_forecast(message: Message) -> None:
        """Возвращает прогноз по введенному городу."""
        city = (message.text or "").strip()
        if not city:
            await message.answer(formatter.format_error("Пустой ввод. Укажите название города."))
            return

        try:
            result = await weather_service.get_forecast_by_city(city=city, extended=False)
            await message.answer(formatter.format_forecast(result, extended=False))
            await state_manager.set_state(message.from_id, WeatherStates.MAIN_MENU)
            await message.answer("Главное меню:", keyboard=get_main_keyboard())
        except CityNotFoundError:
            await message.answer(formatter.format_error("Город не найден. Попробуйте еще раз."))
        except APIConnectionError:
            await message.answer(formatter.format_error("Сервис погоды временно недоступен."))
        except OpenWeatherAPIError as exc:
            logger.exception("Ошибка получения прогноза")
            await message.answer(formatter.format_error(str(exc)))
