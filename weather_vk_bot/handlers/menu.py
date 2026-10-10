"""Обработчики главного меню и навигации."""

from __future__ import annotations

from vkbottle.bot import Bot, Message

from weather_vk_bot.keyboards.main_keyboard import get_main_keyboard
from weather_vk_bot.services.state_manager import StateManager, WeatherStates


def register_menu_handlers(bot: Bot, state_manager: StateManager) -> None:
    """Регистрирует хендлеры главного меню."""

    @bot.on.message(
        text=[
            "/start",
            "start",
            "начать",
            "Начать",
            "меню",
            "Меню",
            "/menu",
            "🏠 Главное меню",
            "⬅️ Назад",
        ]
    )
    async def show_main_menu(message: Message) -> None:
        """Показывает пользователю главное меню."""
        await state_manager.set_state(message.from_id, WeatherStates.MAIN_MENU)
        await state_manager.set_extended_mode(message.from_id, False)
        await message.answer(
            "Привет! Я погодный бот.\nВыберите действие из меню ниже.",
            keyboard=get_main_keyboard(),
        )
