"""Форматирование ответов API в структуру для интеграции в систему."""

from __future__ import annotations

from typing import Any, Dict, List


class WeatherFormatter:
    """Преобразует сырые JSON-данные в стандартный выходной формат."""

    def format_basic_weather(
        self, weather_data: Dict[str, Any], air_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Формирует базовый ответ по текущей погоде."""
        weather_main = (weather_data.get("weather") or [{}])[0]
        main = weather_data.get("main") or {}
        wind = weather_data.get("wind") or {}
        clouds = weather_data.get("clouds") or {}
        sys_data = weather_data.get("sys") or {}

        return {
            "city": weather_data.get("name"),
            "country": sys_data.get("country"),
            "weather_main": weather_main.get("main"),
            "weather_description": weather_main.get("description"),
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "humidity": main.get("humidity"),
            "wind_speed": wind.get("speed"),
            "cloudiness": clouds.get("all"),
            "air_quality": {
                "aqi_index": air_analysis.get("aqi_index"),
                "aqi_label": air_analysis.get("aqi_label"),
                "aqi_label_ru": air_analysis.get("aqi_label_ru"),
                "summary": air_analysis.get("human_summary"),
            },
        }

    def format_extended_weather(
        self, weather_data: Dict[str, Any], air_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Формирует расширенный ответ по текущей погоде."""
        basic = self.format_basic_weather(weather_data, air_analysis)
        main = weather_data.get("main") or {}
        sys_data = weather_data.get("sys") or {}

        basic.update(
            {
                "sunrise": sys_data.get("sunrise"),
                "sunset": sys_data.get("sunset"),
                "pressure": main.get("pressure"),
                "sea_level": main.get("sea_level"),
                "ground_level": main.get("grnd_level"),
                "visibility": weather_data.get("visibility"),
                "air_pollution_analysis": air_analysis,
            }
        )
        return basic

    def format_forecast_data(
        self, forecast_data: Dict[str, Any], air_analysis: Dict[str, Any], extended: bool = False
    ) -> Dict[str, Any]:
        """Формирует ответ по прогнозу на 5 дней."""
        city_data = forecast_data.get("city") or {}
        forecast_list = forecast_data.get("list") or []

        items: List[Dict[str, Any]] = []
        for entry in forecast_list:
            main = entry.get("main") or {}
            weather_main = (entry.get("weather") or [{}])[0]
            clouds = entry.get("clouds") or {}
            wind = entry.get("wind") or {}

            items.append(
                {
                    "datetime": entry.get("dt_txt"),
                    "temperature": main.get("temp"),
                    "humidity": main.get("humidity"),
                    "pressure": main.get("pressure"),
                    "weather_description": weather_main.get("description"),
                    "cloudiness": clouds.get("all"),
                    "wind_speed": wind.get("speed"),
                    "precipitation_probability": entry.get("pop"),
                }
            )

        result: Dict[str, Any] = {
            "city": city_data.get("name"),
            "country": city_data.get("country"),
            "forecast": items,
            "air_quality": {
                "aqi_index": air_analysis.get("aqi_index"),
                "aqi_label": air_analysis.get("aqi_label"),
                "aqi_label_ru": air_analysis.get("aqi_label_ru"),
                "summary": air_analysis.get("human_summary"),
            },
        }

        if extended:
            result.update(
                {
                    "sunrise": city_data.get("sunrise"),
                    "sunset": city_data.get("sunset"),
                    "air_pollution_analysis": air_analysis,
                }
            )

        return result
