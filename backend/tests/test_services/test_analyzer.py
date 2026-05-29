from datetime import date
from pathlib import Path

import pytest

from app.db.database import init_db
from app.db.transaction_repo import insert_transaction
from app.models.transaction import Transaction
from app.services.analyzer import analyze


@pytest.fixture
def db(tmp_path: Path) -> Path:
    p = tmp_path / "test.db"
    init_db(p)
    today = date.today()
    for note, amount, cat in [
        ("cơm trưa", 50_000, "Ăn uống"),
        ("xăng", 100_000, "Di chuyển"),
        ("tiền phòng", 4_000_000, "Nhà ở"),
    ]:
        insert_transaction(
            Transaction(date=today, amount=amount, note=note, category=cat),
            sheet="052026", db_path=p,
        )
    return p


def test_daily_total(db: Path) -> None:
    result = analyze(db_path=db, monthly_budget=20_000_000)
    assert result.daily_total == pytest.approx(4_150_000)


def test_monthly_equals_daily_when_all_today(db: Path) -> None:
    result = analyze(db_path=db, monthly_budget=20_000_000)
    assert result.monthly_total == result.daily_total


def test_top_category(db: Path) -> None:
    result = analyze(db_path=db, monthly_budget=20_000_000)
    assert result.top_category == "Nhà ở"


def test_risk_low(db: Path) -> None:
    result = analyze(db_path=db, monthly_budget=20_000_000)
    assert result.risk_level == "low"   # 4.15M / 20M = 20%


def test_risk_high(db: Path) -> None:
    result = analyze(db_path=db, monthly_budget=4_500_000)
    assert result.risk_level == "high"  # 4.15M / 4.5M = 92%


def test_risk_medium(db: Path) -> None:
    result = analyze(db_path=db, monthly_budget=6_000_000)
    assert result.risk_level == "medium"  # 4.15M / 6M = 69%


def test_empty_db(tmp_path: Path) -> None:
    p = tmp_path / "empty.db"
    init_db(p)
    result = analyze(db_path=p, monthly_budget=20_000_000)
    assert result.monthly_total == 0
    assert result.risk_level == "low"
    assert result.top_category == "—"
