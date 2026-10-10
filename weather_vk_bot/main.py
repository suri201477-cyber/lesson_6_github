"""Точка запуска VK Weather Bot."""

from __future__ import annotations

import logging

from weather_vk_bot.bot import VKWeatherBot, load_bot_config


def setup_logging() -> None:
    """Настраивает базовое логирование приложения."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    """Инициализирует и запускает VK-бота."""
    setup_logging()
    config = load_bot_config()
    app = VKWeatherBot(config=config)
    app.run()


if __name__ == "__main__":
    main()
