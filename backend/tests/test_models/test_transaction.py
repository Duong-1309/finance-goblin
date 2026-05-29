from datetime import date

import pytest
from pydantic import ValidationError

from app.models.transaction import Transaction


def valid_tx(**overrides) -> dict:  # type: ignore[type-arg]
    base = {"date": date(2026, 5, 1), "amount": 120000.0, "note": "cơm trưa", "category": "Ăn uống"}
    base.update(overrides)
    return base


def test_valid_transaction() -> None:
    tx = Transaction(**valid_tx())
    assert tx.amount == 120000.0
    assert tx.category == "Ăn uống"


def test_amount_zero_rejected() -> None:
    with pytest.raises(ValidationError):
        Transaction(**valid_tx(amount=0))


def test_amount_negative_rejected() -> None:
    with pytest.raises(ValidationError):
        Transaction(**valid_tx(amount=-1000))


def test_category_null_rejected() -> None:
    with pytest.raises(ValidationError):
        Transaction(**valid_tx(category="NULL"))


def test_category_header_rejected() -> None:
    with pytest.raises(ValidationError):
        Transaction(**valid_tx(category="Danh mục"))


def test_category_empty_rejected() -> None:
    with pytest.raises(ValidationError):
        Transaction(**valid_tx(category=""))


def test_note_is_stripped() -> None:
    tx = Transaction(**valid_tx(note="  cơm trưa  "))
    assert tx.note == "cơm trưa"


def test_date_parsed() -> None:
    tx = Transaction(**valid_tx(date=date(2026, 1, 5)))
    assert tx.date.month == 1
