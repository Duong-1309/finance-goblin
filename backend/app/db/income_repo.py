from datetime import date
from pathlib import Path

from app.db.database import get_connection


def add_income(
    amount: float,
    source: str,
    note: str = "",
    on_date: date | None = None,
    db_path: Path | None = None,
) -> None:
    d = on_date or date.today()
    month = d.strftime("%Y-%m")
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO income (date, amount, source, note, month) VALUES (?,?,?,?,?)",
            (d.isoformat(), amount, source.strip(), note.strip(), month),
        )


def get_month_income(month: str, db_path: Path | None = None) -> list[dict]:
    """Return all income rows for YYYY-MM month."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT date, amount, source, note FROM income WHERE month = ? ORDER BY date",
            (month,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_month_total(month: str, db_path: Path | None = None) -> float:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM income WHERE month = ?", (month,)
        ).fetchone()
    return float(row[0])
