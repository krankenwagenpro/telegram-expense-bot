"""Telegram bot for personal expense tracking (aiogram 3 + SQLite)."""
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
    "I help you track your expenses.\n\n"
    "/add 500 food - add an expense\n"
    "/month - summary for the current month\n"
    "/last - last 5 expenses\n"
    "/undo - delete the last expense"
)


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer("Hi!\n\n" + HELP_TEXT)


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@dp.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.answer("Usage: /add 500 food")
        return

    parts = command.args.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Please provide an amount and a category: /add 500 food")
        return

    try:
        amount = float(parts[0].replace(",", "."))
    except ValueError:
        await message.answer("The amount must be a number: /add 500 food")
        return

    if amount <= 0:
        await message.answer("The amount must be greater than zero.")
        return

    category = parts[1].strip().lower()
    db.add_expense(message.from_user.id, amount, category)
    await message.answer(f"Saved: {amount:.2f} - {category}")


@dp.message(Command("month"))
async def cmd_month(message: Message) -> None:
    rows = db.get_month_summary(message.from_user.id)
    if not rows:
        await message.answer("No expenses this month yet.")
        return

    total = sum(amount for _, amount in rows)
    lines = [f"{category}: {amount:.2f}" for category, amount in rows]
    await message.answer("This month:\n" + "\n".join(lines) + f"\n\nTotal: {total:.2f}")


@dp.message(Command("last"))
async def cmd_last(message: Message) -> None:
    rows = db.get_last(message.from_user.id)
    if not rows:
        await message.answer("No expenses yet.")
        return

    lines = [
        f"{created[:16].replace('T', ' ')} - {amount:.2f} - {category}"
        for amount, category, created in rows
    ]
    await message.answer("Recent expenses:\n" + "\n".join(lines))


@dp.message(Command("undo"))
async def cmd_undo(message: Message) -> None:
    if db.delete_last(message.from_user.id):
        await message.answer("Last expense deleted.")
    else:
        await message.answer("Nothing to delete.")


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN not found. Create a .env file (see .env.example).")

    db.init_db()
    bot = Bot(token=token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
