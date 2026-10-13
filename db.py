"""SQLite database layer for the expense bot."""
import sqlite3
from contextlib import closing
from datetime import datetime

DB_PATH = "expenses.db"


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create the expenses table if it does not exist."""
    with closing(_connect()) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def add_expense(user_id: int, amount: float, category: str) -> None:
    """Save a new expense for the given Telegram user."""
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, created_at) VALUES (?, ?, ?, ?)",
            (user_id, amount, category, datetime.now().isoformat(timespec="seconds")),
        )


def get_month_summary(user_id: int) -> list[tuple[str, float]]:
    """Return (category, total) pairs for the current month, largest first."""
    month = datetime.now().strftime("%Y-%m")
    with closing(_connect()) as conn:
        return conn.execute(
            """
            SELECT category, SUM(amount) FROM expenses
            WHERE user_id = ? AND created_at LIKE ?
            GROUP BY category ORDER BY SUM(amount) DESC
            """,
            (user_id, f"{month}%"),
        ).fetchall()


def get_last(user_id: int, limit: int = 5) -> list[tuple[float, str, str]]:
    """Return the most recent expenses as (amount, category, created_at)."""
    with closing(_connect()) as conn:
        return conn.execute(
            """
            SELECT amount, category, created_at FROM expenses
            WHERE user_id = ? ORDER BY id DESC LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()


def delete_last(user_id: int) -> bool:
    """Delete the user's latest expense. Return False if there is nothing to delete."""
    with closing(_connect()) as conn, conn:
        row = conn.execute(
            "SELECT id FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        if row is None:
            return False
        conn.execute("DELETE FROM expenses WHERE id = ?", (row[0],))
        return True
