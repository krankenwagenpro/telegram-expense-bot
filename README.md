# Telegram Expense Bot

A Telegram bot for tracking personal expenses. Built with Python, aiogram 3 and SQLite.

## Features
- `/add 500 food` - add an expense
- `/month` - spending summary for the current month, grouped by category
- `/last` - last 5 expenses
- `/undo` - delete the last expense

Each user's data is stored separately (by Telegram user ID).

## Setup
1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Copy `.env.example` to `.env` and paste your token.
3. Install dependencies and run:

```
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

## Project structure
- `bot.py` - bot command handlers
- `db.py` - SQLite data access layer

## Tech stack
Python 3.10+, aiogram 3, SQLite, python-dotenv
