"""Главная клавиатура бота."""

from vkbottle import Keyboard, KeyboardButtonColor, Text


def get_main_keyboard() -> Keyboard:
    """Возвращает главную клавиатуру."""
    keyboard = Keyboard(one_time=False, inline=False)
    keyboard.add(Text("🌤 Погода сейчас"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("📅 Прогноз 5 дней"), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    keyboard.add(Text("📍 Геолокация"), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text("🌫 Расширенный режим"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("ℹ️ Помощь"), color=KeyboardButtonColor.SECONDARY)
    return keyboard
