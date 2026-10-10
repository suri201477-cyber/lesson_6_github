"""Аналитика качества воздуха на основе данных OpenWeather."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .exceptions import OpenWeatherAPIError


@dataclass(frozen=True)
class PollutantThresholds:
    """Пороговые значения загрязнителя для категорий качества воздуха."""

    good: float
    fair: float
    moderate: float
    poor: float


class AirQualityAnalyzer:
    """Выполняет категоризацию и формирует человекочитаемый вывод по воздуху."""

    CATEGORY_ORDER = ("Good", "Fair", "Moderate", "Poor", "Very Poor")
    CATEGORY_LABEL_RU = {
        "Good": "Хорошее",
        "Fair": "Удовлетворительное",
        "Moderate": "Умеренное",
        "Poor": "Плохое",
        "Very Poor": "Очень плохое",
    }
    CATEGORY_SUMMARY_RU = {
        "Good": "Качество воздуха хорошее. Основные загрязнители находятся в безопасных пределах.",
        "Fair": "Качество воздуха удовлетворительное. Зафиксированы незначительные превышения по отдельным загрязнителям.",
        "Moderate": "Качество воздуха умеренное. Рекомендуется ограничить длительное пребывание на улице чувствительным группам.",
        "Poor": "Качество воздуха плохое. Чувствительным группам следует сократить активность на открытом воздухе.",
        "Very Poor": "Качество воздуха очень плохое. Высокий риск для здоровья, рекомендуется минимизировать пребывание на улице.",
    }
    POLLUTANT_RU = {
        "so2": "SO2",
        "no2": "NO2",
        "pm10": "PM10",
        "pm2_5": "PM2.5",
        "o3": "O3",
        "co": "CO",
    }
    POLLUTANT_UNIT = {
        "so2": "мкг/м³",
        "no2": "мкг/м³",
        "pm10": "мкг/м³",
        "pm2_5": "мкг/м³",
        "o3": "мкг/м³",
        "co": "мкг/м³",
    }
    POLLUTANT_THRESHOLDS = {
        "so2": PollutantThresholds(good=20.0, fair=80.0, moderate=250.0, poor=350.0),
        "no2": PollutantThresholds(good=40.0, fair=70.0, moderate=150.0, poor=200.0),
        "pm10": PollutantThresholds(good=20.0, fair=50.0, moderate=100.0, poor=200.0),
        "pm2_5": PollutantThresholds(good=10.0, fair=25.0, moderate=50.0, poor=75.0),
        "o3": PollutantThresholds(good=60.0, fair=100.0, moderate=140.0, poor=180.0),
        "co": PollutantThresholds(good=4400.0, fair=9400.0, moderate=12400.0, poor=15400.0),
    }
    OWM_AQI_LABEL = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor",
    }

    def analyze(self, air_data: Dict[str, Any]) -> Dict[str, Any]:
        """Возвращает расширенный анализ качества воздуха."""
        records = air_data.get("list") or []
        if not records:
            raise OpenWeatherAPIError("Данные о загрязнении воздуха отсутствуют в ответе API.")

        first = records[0]
        components = first.get("components") or {}
        aqi_index = (first.get("main") or {}).get("aqi")

        pollutant_details: Dict[str, Dict[str, Any]] = {}
        categories: List[str] = []
        exceeded_pollutants: List[str] = []

        for pollutant in ("so2", "no2", "pm10", "pm2_5", "o3", "co"):
            if pollutant not in components:
                continue
            value = float(components[pollutant])
            category = self._pollutant_category(pollutant, value)
            categories.append(category)

            pollutant_details[pollutant] = {
                "name": self.POLLUTANT_RU[pollutant],
                "value": value,
                "unit": self.POLLUTANT_UNIT[pollutant],
                "status": category,
                "status_ru": self.CATEGORY_LABEL_RU[category],
            }

            if category != "Good":
                exceeded_pollutants.append(self.POLLUTANT_RU[pollutant])

        if not categories:
            raise OpenWeatherAPIError(
                "Невозможно выполнить анализ воздуха: отсутствуют обязательные компоненты."
            )

        overall_label = self._choose_overall_label(categories, aqi_index)
        summary_base = self.CATEGORY_SUMMARY_RU[overall_label]
        if exceeded_pollutants:
            summary = (
                f"{summary_base} Превышение относительно безопасного уровня: "
                f"{', '.join(exceeded_pollutants)}."
            )
        else:
            summary = summary_base

        return {
            "aqi_index": aqi_index,
            "aqi_label": overall_label,
            "aqi_label_ru": self.CATEGORY_LABEL_RU[overall_label],
            "pollutant_details": pollutant_details,
            "exceeded_pollutants": exceeded_pollutants,
            "human_summary": summary,
        }

    def _pollutant_category(self, pollutant: str, value: float) -> str:
        """Определяет категорию качества для конкретного загрязнителя."""
        threshold = self.POLLUTANT_THRESHOLDS[pollutant]
        if value < threshold.good:
            return "Good"
        if value < threshold.fair:
            return "Fair"
        if value < threshold.moderate:
            return "Moderate"
        if value < threshold.poor:
            return "Poor"
        return "Very Poor"

    def _choose_overall_label(self, categories: List[str], aqi_index: Optional[int]) -> str:
        """Выбирает итоговую категорию по максимуму между AQI и загрязнителями."""
        category_score = max(self.CATEGORY_ORDER.index(cat) for cat in categories)
        category_label = self.CATEGORY_ORDER[category_score]
        if aqi_index is None:
            return category_label

        aqi_label = self.OWM_AQI_LABEL.get(aqi_index)
        if not aqi_label:
            return category_label

        aqi_score = self.CATEGORY_ORDER.index(aqi_label)
        return self.CATEGORY_ORDER[max(category_score, aqi_score)]
