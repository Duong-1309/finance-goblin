from datetime import date
from pathlib import Path

import pytest

from app.db.database import init_db
from app.db.transaction_repo import count_transactions, get_transactions_since, insert_transaction
from app.models.transaction import Transaction


@pytest.fixture
def db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    init_db(db_path)
    return db_path


def make_tx(**overrides) -> Transaction:  # type: ignore[type-arg]
    base = {"date": date(2026, 5, 1), "amount": 120000.0, "note": "cơm trưa", "category": "Ăn uống"}
    base.update(overrides)
    return Transaction(**base)


def test_insert_and_count(db: Path) -> None:
    assert insert_transaction(make_tx(), sheet="052026", db_path=db)
    assert count_transactions(db_path=db) == 1


def test_duplicate_skipped(db: Path) -> None:
    tx = make_tx()
    assert insert_transaction(tx, sheet="052026", db_path=db)
    assert not insert_transaction(tx, sheet="052026", db_path=db)
    assert count_transactions(db_path=db) == 1


def test_get_transactions_since(db: Path) -> None:
    insert_transaction(make_tx(date=date(2026, 4, 1)), sheet="042026", db_path=db)
    insert_transaction(make_tx(date=date(2026, 5, 1)), sheet="052026", db_path=db)
    result = get_transactions_since(date(2026, 5, 1), db_path=db)
    assert len(result) == 1
    assert result[0].date == date(2026, 5, 1)


def test_isolated_test_database(db: Path, tmp_path: Path) -> None:
    other_db = tmp_path / "other.db"
    init_db(other_db)
    insert_transaction(make_tx(), sheet="052026", db_path=db)
    assert count_transactions(db_path=other_db) == 0
