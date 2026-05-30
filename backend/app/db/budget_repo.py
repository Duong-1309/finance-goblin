from pathlib import Path

from app.db.database import get_connection

TOTAL_KEY = "__total__"


def set_budget(category: str, amount: float, db_path: Path | None = None) -> None:
    """Set budget for a category (or overall total using TOTAL_KEY)."""
    with get_connection(db_path) as conn:
        conn.execute(
            """INSERT INTO budgets (category, amount, updated_at)
               VALUES (?, ?, datetime('now'))
               ON CONFLICT(category) DO UPDATE
               SET amount=excluded.amount, updated_at=excluded.updated_at""",
            (category.strip(), amount),
        )


def get_budget(category: str, db_path: Path | None = None) -> float | None:
    """Return budget for a category, or None if not set."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT amount FROM budgets WHERE category = ?", (category.strip(),)
        ).fetchone()
    return float(row["amount"]) if row else None


def get_all_budgets(db_path: Path | None = None) -> dict[str, float]:
    """Return all budgets as {category: amount}."""
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT category, amount FROM budgets ORDER BY category").fetchall()
    return {r["category"]: float(r["amount"]) for r in rows}
