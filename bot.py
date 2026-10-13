"""Telegram-бот для учёта личных расходов (aiogram 3 + SQLite)."""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

import db

load_dotenv()
logging.basicConfig(level=logging.INFO)

dp = Dispatcher()

HELP_TEXT = (
    "Я помогаю вести учёт расходов.\n\n"
    "/add 500 еда — добавить трату\n"
    "/month — итоги за текущий месяц\n"
    "/last — последние 5 трат\n"
    "/undo — удалить последнюю трату"
)


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer("Привет!\n\n" + HELP_TEXT)


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@dp.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.answer("Формат: /add 500 еда")
        return

    parts = command.args.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажите сумму и категорию: /add 500 еда")
        return

    try:
        amount = float(parts[0].replace(",", "."))
    except ValueError:
        await message.answer("Сумма должна быть числом: /add 500 еда")
        return

    if amount <= 0:
        await message.answer("Сумма должна быть больше нуля.")
        return

    category = parts[1].strip().lower()
    db.add_expense(message.from_user.id, amount, category)
    await message.answer(f"Записано: {amount:.2f} ₽ — {category}")


@dp.message(Command("month"))
async def cmd_month(message: Message) -> None:
    rows = db.get_month_summary(message.from_user.id)
    if not rows:
        await message.answer("В этом месяце трат пока нет.")
        return

    total = sum(amount for _, amount in rows)
    lines = [f"{category}: {amount:.2f} ₽" for category, amount in rows]
    await message.answer("Расходы за месяц:\n" + "\n".join(lines) + f"\n\nИтого: {total:.2f} ₽")


@dp.message(Command("last"))
async def cmd_last(message: Message) -> None:
    rows = db.get_last(message.from_user.id)
    if not rows:
        await message.answer("Трат пока нет.")
        return

    lines = [f"{created[:16].replace('T', ' ')} — {amount:.2f} ₽ — {category}"
             for amount, category, created in rows]
    await message.answer("Последние траты:\n" + "\n".join(lines))


@dp.message(Command("undo"))
async def cmd_undo(message: Message) -> None:
    if db.delete_last(message.from_user.id):
        await message.answer("Последняя трата удалена.")
    else:
        await message.answer("Удалять нечего.")


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("Не найден BOT_TOKEN. Создайте файл .env (см. .env.example).")

    db.init_db()
    bot = Bot(token=token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
