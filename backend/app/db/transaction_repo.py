from datetime import date
from pathlib import Path

from app.db.database import get_connection
from app.models.transaction import Transaction


def insert_transaction(tx: Transaction, sheet: str, db_path: Path | None = None) -> bool:
    """Insert transaction. Returns False if duplicate (skipped)."""
    with get_connection(db_path) as conn:
        try:
            conn.execute(
                "INSERT INTO transactions (date, amount, note, category, sheet) VALUES (?,?,?,?,?)",
                (tx.date.isoformat(), tx.amount, tx.note, tx.category, sheet),
            )
            return True
        except Exception:
            return False


def get_transactions_since(since: date, db_path: Path | None = None) -> list[Transaction]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT date, amount, note, category FROM transactions WHERE date >= ? ORDER BY date",
            (since.isoformat(),),
        ).fetchall()
    return [
        Transaction(date=r["date"], amount=r["amount"], note=r["note"], category=r["category"])
        for r in rows
    ]


def count_transactions(db_path: Path | None = None) -> int:
    with get_connection(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
