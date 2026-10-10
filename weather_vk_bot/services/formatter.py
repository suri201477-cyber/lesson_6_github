"""Форматирование ответов погоды и ошибок для сообщений VK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List


class WeatherFormatter:
    """Преобразует данные API в читабельные сообщения с хорошим UX."""

    divider = "──────────────"

    @staticmethod
    def _kelvin_to_celsius(value: Any) -> str:
        """Конвертирует температуру из Кельвинов в строку градусов Цельсия."""
        if value is None:
            return "н/д"
        return f"{round(float(value) - 273.15):+d}°C"

    @staticmethod
    def _wind_to_text(value: Any) -> str:
        """Форматирует скорость ветра."""
        if value is None:
            return "н/д"
        return f"{float(value):.1f} м/с"

    @staticmethod
    def _to_percent(value: Any) -> str:
        """Форматирует процентные значения."""
        if value is None:
            return "н/д"
        return f"{int(value)}%"

    @staticmethod
    def _unix_to_hhmm(value: Any) -> str:
        """Преобразует Unix timestamp в локальное время HH:MM."""
        if value is None:
            return "н/д"
        return datetime.fromtimestamp(int(value)).strftime("%H:%M")

    def format_current(self, data: Dict[str, Any], extended: bool = False) -> str:
        """Форматирует текущую погоду."""
        lines = [
            f"🌍 Город: {data.get('city', 'н/д')}",
            f"🌤 Погода: {data.get('weather_description', 'н/д')}",
            f"🌡 Температура: {self._kelvin_to_celsius(data.get('temperature'))}",
            f"🤗 Ощущается как: {self._kelvin_to_celsius(data.get('feels_like'))}",
            f"💧 Влажность: {self._to_percent(data.get('humidity'))}",
            f"💨 Ветер: {self._wind_to_text(data.get('wind_speed'))}",
            f"☁ Облачность: {self._to_percent(data.get('cloudiness'))}",
            self.divider,
            f"🌫 Воздух: {data.get('air_quality', {}).get('aqi_label', 'н/д')}",
            f"💬 {data.get('air_quality', {}).get('summary', 'Нет данных по воздуху.')}",
        ]

        if not extended:
            return "\n".join(lines)

        air_analysis = data.get("air_pollution_analysis", {})
        pollutants = air_analysis.get("pollutant_details", {})
        exceed = air_analysis.get("exceeded_pollutants", [])

        lines.extend(
            [
                self.divider,
                "📌 Расширенная аналитика",
                f"🌅 Рассвет: {self._unix_to_hhmm(data.get('sunrise'))}",
                f"🌇 Закат: {self._unix_to_hhmm(data.get('sunset'))}",
                f"🧭 Давление: {data.get('pressure', 'н/д')} гПа",
                f"🌊 Уровень моря: {data.get('sea_level', 'н/д')}",
                f"🏔 Уровень земли: {data.get('ground_level', 'н/д')}",
                f"👁 Видимость: {data.get('visibility', 'н/д')} м",
                self.divider,
                f"🌫 AQI: {air_analysis.get('aqi_index', 'н/д')} ({air_analysis.get('aqi_label', 'н/д')})",
                "📊 Загрязнители:",
                self._format_pollutants(pollutants.values()),
                (
                    "⚠ Выход за безопасный уровень: " + ", ".join(exceed)
                    if exceed
                    else "✅ Все основные загрязнители в безопасном диапазоне."
                ),
                f"💬 {air_analysis.get('human_summary', 'Нет аналитики воздуха.')}",
            ]
        )
        return "\n".join(lines)

    def format_forecast(self, data: Dict[str, Any], extended: bool = False) -> str:
        """Форматирует прогноз на 5 дней."""
        header = [
            f"📅 Прогноз на 5 дней для: {data.get('city', 'н/д')}",
            self.divider,
        ]

        entries: List[str] = []
        for item in data.get("forecast", [])[:10]:
            entries.append(
                (
                    f"🕒 {item.get('datetime', 'н/д')}\n"
                    f"  🌡 {self._kelvin_to_celsius(item.get('temperature'))} | "
                    f"💧 {self._to_percent(item.get('humidity'))} | "
                    f"💨 {self._wind_to_text(item.get('wind_speed'))}\n"
                    f"  🌤 {item.get('weather_description', 'н/д')}, "
                    f"☁ {self._to_percent(item.get('cloudiness'))}, "
                    f"☔ {self._to_percent((item.get('precipitation_probability') or 0) * 100)}"
                )
            )

        footer = [
            self.divider,
            f"🌫 Воздух: {data.get('air_quality', {}).get('aqi_label', 'н/д')}",
            f"💬 {data.get('air_quality', {}).get('summary', 'Нет данных по воздуху.')}",
        ]
        if extended:
            footer.extend(
                [
                    f"🌅 Рассвет: {self._unix_to_hhmm(data.get('sunrise'))}",
                    f"🌇 Закат: {self._unix_to_hhmm(data.get('sunset'))}",
                ]
            )
        return "\n".join(header + entries + footer)

    def format_help(self) -> str:
        """Возвращает справку по командам и сценариям использования."""
        return (
            "ℹ️ Помощь по Weather Bot\n"
            "──────────────\n"
            "• 🌤 Погода сейчас — текущие данные по городу\n"
            "• 📅 Прогноз 5 дней — подробный прогноз по городу\n"
            "• 📍 Геолокация — отправьте гео или координаты (55.7558, 37.6173)\n"
            "• 🌫 Расширенный режим — включает детальную аналитику\n"
            "──────────────\n"
            "Для возврата используйте кнопки ⬅️ Назад и 🏠 Главное меню."
        )

    def format_error(self, message: str) -> str:
        """Форматирует сообщение об ошибке для пользователя."""
        return f"❌ Ошибка: {message}"

    def _format_pollutants(self, details: Iterable[Dict[str, Any]]) -> str:
        """Форматирует список загрязнителей для расширенного режима."""
        lines = []
        for item in details:
            lines.append(
                f"  • {item.get('name', 'n/a')}: {item.get('value', 'n/a')} "
                f"{item.get('unit', '')} ({item.get('status', 'n/a')})"
            )
        return "\n".join(lines) if lines else "  • Нет данных по загрязнителям"
