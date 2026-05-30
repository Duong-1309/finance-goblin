from pathlib import Path

from app.db.database import get_connection


def set_allocation(month: str, category: str, amount: float, db_path: Path | None = None) -> None:
    """Set allocation. If amount=0, delete the entry."""
    if amount <= 0:
        delete_allocation(month, category, db_path)
        return
    with get_connection(db_path) as conn:
        conn.execute(
            """INSERT INTO budget_allocations (month, category, amount) VALUES (?,?,?)
               ON CONFLICT(month, category) DO UPDATE SET amount=excluded.amount""",
            (month, category.strip(), amount),
        )


def delete_allocation(month: str, category: str, db_path: Path | None = None) -> bool:
    """Delete a specific allocation. Returns True if something was deleted."""
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM budget_allocations WHERE month=? AND category=?",
            (month, category.strip()),
        )
        return cur.rowcount > 0


def clear_allocations(month: str, db_path: Path | None = None) -> int:
    """Delete all allocations for a month. Returns count deleted."""
    with get_connection(db_path) as conn:
        cur = conn.execute("DELETE FROM budget_allocations WHERE month=?", (month,))
        return cur.rowcount


def get_allocations(month: str, db_path: Path | None = None) -> dict[str, float]:
    """Return {category: amount} for a month."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT category, amount FROM budget_allocations WHERE month = ? ORDER BY category",
            (month,),
        ).fetchall()
    return {r["category"]: float(r["amount"]) for r in rows}


def get_allocation_total(month: str, db_path: Path | None = None) -> float:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM budget_allocations WHERE month = ?", (month,)
        ).fetchone()
    return float(row[0])
