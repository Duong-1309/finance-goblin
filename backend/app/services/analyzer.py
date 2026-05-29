from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from app.core.config import settings
from app.db.database import get_connection


@dataclass
class AnalysisResult:
    daily_total: float
    weekly_total: float
    monthly_total: float
    top_category: str
    top_category_amount: float
    budget_usage_pct: float  # monthly_total / monthly_budget * 100
    risk_level: str  # low / medium / high
    recent_items: list[dict] = field(default_factory=list)


def analyze(db_path: Path | None = None, monthly_budget: float | None = None) -> AnalysisResult:
    db_path = db_path or Path(settings.db_path)
    budget = monthly_budget or float(getattr(settings, "monthly_budget", 20_000_000))

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    with get_connection(db_path) as conn:

        def total_since(since: date) -> float:
            row = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE date >= ?",
                (since.isoformat(),),
            ).fetchone()
            return float(row[0])

        daily = total_since(today)
        weekly = total_since(week_start)
        monthly = total_since(month_start)

        # Top category this month
        cat_rows = conn.execute(
            """SELECT category, SUM(amount) as total
               FROM transactions WHERE date >= ?
               GROUP BY category ORDER BY total DESC LIMIT 1""",
            (month_start.isoformat(),),
        ).fetchone()
        top_cat = cat_rows["category"] if cat_rows else "—"
        top_cat_amount = float(cat_rows["total"]) if cat_rows else 0.0

        # Recent items (last 3)
        recent = conn.execute(
            """SELECT date, note, amount, category FROM transactions
               ORDER BY date DESC, rowid DESC LIMIT 3""",
        ).fetchall()

    usage_pct = (monthly / budget * 100) if budget > 0 else 0

    if usage_pct < 50:
        risk = "low"
    elif usage_pct < 85:
        risk = "medium"
    else:
        risk = "high"

    return AnalysisResult(
        daily_total=daily,
        weekly_total=weekly,
        monthly_total=monthly,
        top_category=top_cat,
        top_category_amount=top_cat_amount,
        budget_usage_pct=usage_pct,
        risk_level=risk,
        recent_items=[dict(r) for r in recent],
    )
