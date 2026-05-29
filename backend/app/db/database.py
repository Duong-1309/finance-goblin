import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from app.core.config import settings

CREATE_TRANSACTIONS = """
CREATE TABLE IF NOT EXISTS transactions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    date      TEXT    NOT NULL,
    amount    REAL    NOT NULL,
    note      TEXT    NOT NULL,
    category  TEXT    NOT NULL,
    sheet     TEXT    NOT NULL,
    UNIQUE(date, amount, note, sheet)
)
"""

CREATE_GENERATED_MESSAGES = """
CREATE TABLE IF NOT EXISTS generated_messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    line1      TEXT    NOT NULL,
    line2      TEXT    NOT NULL,
    mood       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
)
"""


def get_db_path() -> Path:
    return Path(settings.db_path)


def init_db(db_path: Path | None = None) -> None:
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute(CREATE_TRANSACTIONS)
        conn.execute(CREATE_GENERATED_MESSAGES)
        conn.commit()


@contextmanager
def get_connection(db_path: Path | None = None) -> Generator[sqlite3.Connection, None, None]:
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
