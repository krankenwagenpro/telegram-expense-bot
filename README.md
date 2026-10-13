# Telegram Expense Bot

Telegram-бот для учёта личных расходов. Python, aiogram 3, SQLite.

## Возможности
- `/add 500 еда` — добавить трату
- `/month` — итоги за текущий месяц по категориям
- `/last` — последние 5 трат
- `/undo` — удалить последнюю трату

Данные каждого пользователя хранятся отдельно (по Telegram user id).

## Запуск
1. Создайте бота у [@BotFather](https://t.me/BotFather) и получите токен.
2. Скопируйте `.env.example` в `.env` и вставьте токен.
3. Установите зависимости и запустите:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

## Структура
- `bot.py` — обработчики команд бота
- `db.py` — работа с базой SQLite
