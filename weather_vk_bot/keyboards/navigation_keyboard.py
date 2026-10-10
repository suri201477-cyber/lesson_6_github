"""Навигационные клавиатуры для переходов и справки."""

from vkbottle import Callback, Keyboard, KeyboardButtonColor, OpenLink, Text


def get_navigation_keyboard() -> Keyboard:
    """Возвращает обычную навигационную клавиатуру."""
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("⬅️ Назад"), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text("🏠 Главное меню"), color=KeyboardButtonColor.PRIMARY)
    return keyboard


def get_help_inline_keyboard() -> Keyboard:
    """Возвращает inline-клавиатуру со ссылкой и callback-кнопкой."""
    keyboard = Keyboard(one_time=False, inline=True)
    keyboard.add(
        OpenLink(
            label="📘 VKBottle",
            link="https://vkbottle.readthedocs.io/ru/latest/tutorial/",
        )
    )
    keyboard.row()
    keyboard.add(
        Callback(label="🏠 Главное меню", payload={"action": "main_menu"}),
        color=KeyboardButtonColor.PRIMARY,
    )
    return keyboard
