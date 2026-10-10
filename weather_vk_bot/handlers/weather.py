"""Сценарий текущей погоды по городу и расширенного режима."""

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


def register_weather_handlers(
    bot: Bot,
    weather_service: WeatherService,
    formatter: WeatherFormatter,
    state_manager: StateManager,
) -> None:
    """Регистрирует хендлеры для текущей погоды."""

    @bot.on.message(text="🌤 Погода сейчас")
    async def request_city_for_weather(message: Message) -> None:
        """Переводит пользователя в состояние ожидания города для текущей погоды."""
        await state_manager.set_state(message.from_id, WeatherStates.WAITING_CITY)
        await state_manager.set_extended_mode(message.from_id, False)
        await message.answer("Введите город:", keyboard=get_navigation_keyboard())

    @bot.on.message(text="🌫 Расширенный режим")
    async def request_city_for_extended_weather(message: Message) -> None:
        """Переводит пользователя в режим расширенной аналитики по городу."""
        await state_manager.set_state(message.from_id, WeatherStates.WAITING_EXTENDED)
        await state_manager.set_extended_mode(message.from_id, True)
        await message.answer(
            "Введите город для расширенного отчета:",
            keyboard=get_navigation_keyboard(),
        )

    @bot.on.message(state=WeatherStates.WAITING_CITY)
    async def handle_city_weather(message: Message) -> None:
        """Возвращает текущую погоду по введенному городу."""
        city = (message.text or "").strip()
        if not city:
            await message.answer(formatter.format_error("Пустой ввод. Укажите название города."))
            return

        try:
            result = await weather_service.get_current_by_city(city=city, extended=False)
            await message.answer(formatter.format_current(result, extended=False))
            await state_manager.set_state(message.from_id, WeatherStates.MAIN_MENU)
            await message.answer("Главное меню:", keyboard=get_main_keyboard())
        except CityNotFoundError:
            await message.answer(formatter.format_error("Город не найден. Попробуйте еще раз."))
        except APIConnectionError:
            await message.answer(formatter.format_error("Сервис погоды временно недоступен."))
        except OpenWeatherAPIError as exc:
            logger.exception("Ошибка получения погоды по городу")
            await message.answer(formatter.format_error(str(exc)))

    @bot.on.message(state=WeatherStates.WAITING_EXTENDED)
    async def handle_city_extended(message: Message) -> None:
        """Возвращает расширенную погоду по введенному городу."""
        city = (message.text or "").strip()
        if not city:
            await message.answer(formatter.format_error("Пустой ввод. Укажите название города."))
            return

        try:
            extended = await state_manager.get_extended_mode(message.from_id)
            result = await weather_service.get_current_by_city(city=city, extended=extended)
            await message.answer(formatter.format_current(result, extended=extended))
            await state_manager.set_extended_mode(message.from_id, False)
            await state_manager.set_state(message.from_id, WeatherStates.MAIN_MENU)
            await message.answer("Главное меню:", keyboard=get_main_keyboard())
        except CityNotFoundError:
            await message.answer(formatter.format_error("Город не найден. Попробуйте еще раз."))
        except APIConnectionError:
            await message.answer(formatter.format_error("Сервис погоды временно недоступен."))
        except OpenWeatherAPIError as exc:
            logger.exception("Ошибка получения расширенной погоды")
            await message.answer(formatter.format_error(str(exc)))
