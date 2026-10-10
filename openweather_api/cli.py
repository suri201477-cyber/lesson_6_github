"""CLI-точка входа для запуска клиента OpenWeather API из консоли."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Dict

from .client import OpenWeatherAPI
from .exceptions import OpenWeatherAPIError
from .utils import to_pretty_json


def _build_parser() -> argparse.ArgumentParser:
    """Создает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Консольный клиент OpenWeather API")
    parser.add_argument("--api-key", dest="api_key", help="API-ключ OpenWeather")
    parser.add_argument("--timeout", type=int, default=15, help="Таймаут HTTP-запросов (сек)")
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Вернуть расширенный набор полей",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    weather_city = subparsers.add_parser("weather-city", help="Погода по названию города")
    weather_city.add_argument("--city", required=True, help="Название города")

    forecast_city = subparsers.add_parser("forecast-city", help="Прогноз по названию города")
    forecast_city.add_argument("--city", required=True, help="Название города")

    weather_coords = subparsers.add_parser("weather-coords", help="Погода по координатам")
    weather_coords.add_argument("--lat", type=float, required=True, help="Широта")
    weather_coords.add_argument("--lon", type=float, required=True, help="Долгота")

    return parser


def _execute(args: argparse.Namespace) -> Dict[str, Any]:
    """Выполняет CLI-команду и возвращает словарь результата."""
    with OpenWeatherAPI(api_key=args.api_key, timeout=args.timeout) as client:
        if args.command == "weather-city":
            return client.get_weather_by_city(city=args.city, extended=args.extended)
        if args.command == "forecast-city":
            return client.get_forecast_by_city(city=args.city, extended=args.extended)
        if args.command == "weather-coords":
            return client.get_weather_by_coordinates(
                lat=args.lat, lon=args.lon, extended=args.extended
            )
    raise OpenWeatherAPIError("Неизвестная команда CLI.")


def _print_menu() -> None:
    """Печатает интерактивное меню."""
    print("\nМеню прогноза погоды:")
    print("1. Текущая погода по городу")
    print("2. Прогноз на 5 дней по городу")
    print("3. Погода по координатам")
    print("4. Выход")


def _ask_extended() -> bool:
    """Запрашивает у пользователя необходимость расширенного вывода."""
    value = input("Расширенный вывод? (y/n): ").strip().lower()
    return value in {"y", "yes", "д", "да"}


def _run_menu(api_key: str | None, timeout: int) -> int:
    """Запускает интерактивное меню и выполняет выбранные операции."""
    with OpenWeatherAPI(api_key=api_key, timeout=timeout) as client:
        while True:
            _print_menu()
            choice = input("Выберите пункт меню (1-4): ").strip()

            try:
                if choice == "1":
                    city = input("Введите город: ").strip()
                    result = client.get_weather_by_city(city=city, extended=_ask_extended())
                    print(to_pretty_json(result))
                elif choice == "2":
                    city = input("Введите город: ").strip()
                    result = client.get_forecast_by_city(city=city, extended=_ask_extended())
                    print(to_pretty_json(result))
                elif choice == "3":
                    lat = float(input("Введите широту: ").strip())
                    lon = float(input("Введите долготу: ").strip())
                    result = client.get_weather_by_coordinates(
                        lat=lat,
                        lon=lon,
                        extended=_ask_extended(),
                    )
                    print(to_pretty_json(result))
                elif choice == "4":
                    print("Выход из программы.")
                    return 0
                else:
                    print("Некорректный пункт меню. Введите число от 1 до 4.")
            except ValueError:
                print("Ошибка: широта и долгота должны быть числами.")
            except OpenWeatherAPIError as exc:
                print(f"Ошибка: {exc}")


def main() -> int:
    """Точка входа CLI-приложения."""
    if len(sys.argv) == 1:
        try:
            return _run_menu(api_key=None, timeout=15)
        except OpenWeatherAPIError as exc:
            print(f"Ошибка: {exc}")
            return 1

    parser = _build_parser()
    args = parser.parse_args()
    try:
        result = _execute(args)
        print(to_pretty_json(result))
        return 0
    except OpenWeatherAPIError as exc:
        print(f"Ошибка: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
