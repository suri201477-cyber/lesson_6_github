"""Обработчики помощи и пользовательской справки."""

from __future__ import annotations

from vkbottle.bot import Bot, Message

from weather_vk_bot.keyboards.navigation_keyboard import get_help_inline_keyboard
from weather_vk_bot.services.formatter import WeatherFormatter


def register_help_handlers(bot: Bot, formatter: WeatherFormatter) -> None:
    """Регистрирует хендлеры раздела помощи."""

    @bot.on.message(text="ℹ️ Помощь")
    async def show_help(message: Message) -> None:
        """Показывает подсказки по работе с ботом."""
        await message.answer(
            formatter.format_help(),
            keyboard=get_help_inline_keyboard(),
        )
