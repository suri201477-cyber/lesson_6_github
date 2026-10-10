"""Основной класс VKWeatherBot и сборка зависимостей."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from vkbottle import CtxStorage
from vkbottle.bot import Bot

from OpenWeatherAPI import OpenWeatherAPI
from weather_vk_bot.handlers.forecast import register_forecast_handlers
from weather_vk_bot.handlers.geo import register_geo_handlers
from weather_vk_bot.handlers.help import register_help_handlers
from weather_vk_bot.handlers.menu import register_menu_handlers
from weather_vk_bot.handlers.weather import register_weather_handlers
from weather_vk_bot.services.formatter import WeatherFormatter
from weather_vk_bot.services.state_manager import StateManager
from weather_vk_bot.services.weather_service import WeatherService


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotConfig:
    """Конфигурация запуска VK-бота."""

    vk_bot_token: str
    openweather_api_key: str


def load_bot_config() -> BotConfig:
    """Загружает конфигурацию из .env."""
    load_dotenv()
    vk_bot_token = os.getenv("VK_BOT_TOKEN")
    openweather_api_key = os.getenv("OPENWEATHER_API_KEY")

    if not vk_bot_token:
        raise ValueError("Не задан VK_BOT_TOKEN в .env")
    if not openweather_api_key:
        raise ValueError("Не задан OPENWEATHER_API_KEY в .env")

    return BotConfig(
        vk_bot_token=vk_bot_token,
        openweather_api_key=openweather_api_key,
    )


class VKWeatherBot:
    """Production-ready бот сообщества VK для работы с погодой."""

    def __init__(self, config: BotConfig) -> None:
        """Создает экземпляр бота и его сервисов."""
        self.config = config
        self.bot = Bot(token=self.config.vk_bot_token)
        self.ctx_storage = CtxStorage()

        weather_api = OpenWeatherAPI(api_key=self.config.openweather_api_key)
        self.weather_service = WeatherService(weather_api)
        self.formatter = WeatherFormatter()
        self.state_manager = StateManager(bot=self.bot, ctx_storage=self.ctx_storage)

        self._register_handlers()

    def _register_handlers(self) -> None:
        """Регистрирует все пользовательские сценарии."""
        register_menu_handlers(self.bot, self.state_manager)
        register_weather_handlers(
            self.bot,
            self.weather_service,
            self.formatter,
            self.state_manager,
        )
        register_forecast_handlers(
            self.bot,
            self.weather_service,
            self.formatter,
            self.state_manager,
        )
        register_geo_handlers(
            self.bot,
            self.weather_service,
            self.formatter,
            self.state_manager,
        )
        register_help_handlers(self.bot, self.formatter)

    def run(self) -> None:
        """Запускает Long Poll обработку сообщений."""
        logger.info("VK Weather Bot запущен.")
        self.bot.run_forever()
