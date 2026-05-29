from datetime import date

from pydantic import BaseModel, field_validator

INVALID_CATEGORIES = {"", "null", "danh mục", "thời gian"}


class Transaction(BaseModel):
    date: date
    amount: float
    note: str
    category: str

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v: str) -> str:
        if v.strip().lower() in INVALID_CATEGORIES:
            raise ValueError(f"invalid category: {v!r}")
        return v.strip()

    @field_validator("note")
    @classmethod
    def note_stripped(cls, v: str) -> str:
        return v.strip()
