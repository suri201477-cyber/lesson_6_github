# VK Weather Bot (VKBottle + OpenWeather)

Production-ready погодный бот для сообщества ВКонтакте на базе **VKBottle**.  
Бот использует модуль `OpenWeatherAPI` как backend-слой и предоставляет удобный кнопочный интерфейс, FSM-состояния, геолокацию и расширенную аналитику качества воздуха.

---

## Возможности

- Текущая погода по городу (`🌤 Погода сейчас`)
- Прогноз на 5 дней (`📅 Прогноз 5 дней`)
- Погода по геолокации VK (`📍 Геолокация`)
- Fallback на ввод координат текстом:  
  - `55.7558,37.6173`  
  - `55.7558 37.6173`
- Расширенный режим (`🌫 Расширенный режим`):
  - рассвет/закат
  - давление, видимость
  - AQI и загрязнители
  - человекочитаемая аналитика воздуха
- Навигация:
  - `⬅️ Назад`
  - `🏠 Главное меню`
- Сервисная архитектура с разделением ответственности:
  - handlers / services / keyboards

---

## Технологии

- Python 3.11+
- [vkbottle](https://github.com/vkbottle/vkbottle)
- requests
- python-dotenv
- logging
- OOP
- FSM (StateDispenser)

---

## Структура проекта

```text
LESSON_VPd04/
├─ main.py
├─ README.md
├─ requirements.txt
├─ .env
├─ OpenWeatherAPI.py
├─ openweather_api/
│  ├─ __init__.py
│  ├─ __main__.py
│  ├─ cli.py
│  ├─ client.py
│  ├─ config.py
│  ├─ exceptions.py
│  ├─ utils.py
│  ├─ services.py
│  ├─ formatters.py
│  ├─ air_quality.py
│  ├─ http_client.py
│  └─ endpoints.py
└─ weather_vk_bot/
   ├─ __init__.py
   ├─ main.py
   ├─ bot.py
   ├─ handlers/
   │  ├─ __init__.py
   │  ├─ menu.py
   │  ├─ weather.py
   │  ├─ forecast.py
   │  ├─ geo.py
   │  └─ help.py
   ├─ services/
   │  ├─ __init__.py
   │  ├─ weather_service.py
   │  ├─ formatter.py
   │  └─ state_manager.py
   └─ keyboards/
      ├─ __init__.py
      ├─ main_keyboard.py
      └─ navigation_keyboard.py
```

---

## Установка

1. Установите зависимости:

```bash
python -m pip install -r requirements.txt
```

2. Создайте/обновите `.env`:

```env
VK_BOT_TOKEN=your_vk_group_token
OPENWEATHER_API_KEY=your_openweather_api_key
```

> Важно: используйте **токен сообщества VK**, а не пользовательский токен.

---

## Настройка VK-сообщества

Перед запуском в настройках сообщества VK включите:

- Сообщения сообщества
- Боты
- Long Poll API
- Событие `message_new`  
  (и при необходимости `message_event` для callback-событий)

---

## Запуск

### Основной запуск

```bash
python main.py
```

### Альтернативно

```bash
python -m weather_vk_bot.main
```

После запуска отправьте в диалог сообщества:

- `/start`
- `start`
- `Начать`
- `Меню`

Бот отправит главное меню с кнопками.

---

## Пользовательские сценарии

### 1) Текущая погода

1. Нажмите `🌤 Погода сейчас`
2. Введите город (например, `Москва`)
3. Получите текущую погоду и краткий отчет по воздуху

### 2) Прогноз на 5 дней

1. Нажмите `📅 Прогноз 5 дней`
2. Введите город
3. Получите прогноз и сводку по качеству воздуха

### 3) Геолокация

1. Нажмите `📍 Геолокация`
2. Отправьте гео из VK
3. Если гео недоступно, введите координаты текстом:
   - `55.7558, 37.6173`
   - `55.7558 37.6173`

### 4) Расширенный режим

1. Нажмите `🌫 Расширенный режим`
2. Введите город
3. Получите расширенный отчет:
   - рассвет/закат
   - давление/видимость
   - AQI и загрязнители
   - аналитическое текстовое пояснение

---

## FSM-состояния

Используются состояния:

- `MAIN_MENU`
- `WAITING_CITY`
- `WAITING_FORECAST_CITY`
- `WAITING_GEO`
- `WAITING_EXTENDED`

Управление вынесено в `weather_vk_bot/services/state_manager.py`.

---

## Обработка ошибок

Бот обрабатывает:

- пустой ввод
- неверный формат координат
- город не найден
- недоступность OpenWeather API
- ошибки геолокации

Ошибки форматируются в user-friendly виде и возвращаются в чат.

---

## Масштабирование

Текущая архитектура уже подготовлена для добавления:

- подписок на погоду
- ежедневных уведомлений
- избранных городов
- персональных настроек пользователя
- мультиязычности
- алертов о плохом воздухе

---

## Полезные команды для отладки

Проверка зависимостей:

```bash
python -m pip install -r requirements.txt
```

Проверка импорта VKBottle:

```bash
python -c "import vkbottle; print('vkbottle import: OK')"
```

---

## Документация

- VKBottle API: https://vkbottle.readthedocs.io/ru/latest/low-level/api/
- VKBottle Tutorial: https://vkbottle.readthedocs.io/ru/latest/tutorial/

