"""Управление состояниями пользователя через StateDispenser и CtxStorage."""

from __future__ import annotations

import inspect
from typing import Any, Dict, Optional

from vkbottle import BaseStateGroup, CtxStorage
from vkbottle.bot import Bot


class WeatherStates(BaseStateGroup):
    """FSM-состояния погодного бота."""

    MAIN_MENU = "main_menu"
    WAITING_CITY = "waiting_city_weather"
    WAITING_FORECAST_CITY = "waiting_city_forecast"
    WAITING_GEO = "waiting_geo"
    WAITING_EXTENDED = "waiting_extended_city"


class StateManager:
    """Единая точка работы с состоянием и пользовательским контекстом."""

    _EXTENDED_KEY = "extended_mode"

    def __init__(self, bot: Bot, ctx_storage: CtxStorage) -> None:
        """Инициализирует менеджер состояния.

        Args:
            bot: Экземпляр VKBottle Bot.
            ctx_storage: Хранилище контекста (CtxStorage) для пользовательских флагов.
        """
        self.bot = bot
        self.ctx_storage = ctx_storage
        self._fallback_flags: Dict[int, Dict[str, Any]] = {}

    async def set_state(self, user_id: int, state: WeatherStates) -> None:
        """Устанавливает FSM-состояние пользователя."""
        dispenser = self.bot.state_dispenser
        try:
            await dispenser.set(peer_id=user_id, state=state)
        except TypeError:
            await dispenser.set(user_id, state)

    async def clear_state(self, user_id: int) -> None:
        """Сбрасывает FSM-состояние пользователя."""
        dispenser = self.bot.state_dispenser
        try:
            await dispenser.delete(peer_id=user_id)
        except TypeError:
            await dispenser.delete(user_id)

    async def set_extended_mode(self, user_id: int, enabled: bool) -> None:
        """Сохраняет флаг расширенного режима для пользователя."""
        key = f"user:{user_id}:{self._EXTENDED_KEY}"
        try:
            result = self.ctx_storage.set(key, enabled)
            if inspect.isawaitable(result):
                await result
        except Exception:
            self._fallback_flags.setdefault(user_id, {})[self._EXTENDED_KEY] = enabled

    async def get_extended_mode(self, user_id: int) -> bool:
        """Возвращает состояние расширенного режима пользователя."""
        key = f"user:{user_id}:{self._EXTENDED_KEY}"
        try:
            value = self.ctx_storage.get(key)
            if inspect.isawaitable(value):
                value = await value
            return bool(value)
        except Exception:
            return bool(
                self._fallback_flags.get(user_id, {}).get(self._EXTENDED_KEY, False)
            )

    async def reset_user_context(self, user_id: int) -> None:
        """Очищает пользовательское состояние и контекстные флаги."""
        await self.clear_state(user_id)
        await self.set_extended_mode(user_id, False)
