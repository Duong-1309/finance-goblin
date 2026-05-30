import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import gspread
from pydantic import ValidationError

from app.core.config import settings
from app.db.database import init_db
from app.db.transaction_repo import insert_transaction
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

# MM/YYYY format — rejects HANOI, VUNGTAU-8/3, etc.
_MONTHLY_SHEET_RE = re.compile(r"^\d{2}/\d{4}$")


@dataclass
class SyncResult:
    imported: int = 0
    skipped: int = 0
    failed: int = 0


def _is_new_format(header_row: list[str]) -> bool:
    """New format has 'Danh mục' as 4th column."""
    return len(header_row) >= 4 and header_row[3].strip() == "Danh mục"


def _parse_amount(raw: str) -> float:
    """Parse '10,000,000' or '1,560,000.00' → float."""
    return float(raw.replace(",", "").strip())


def _parse_date(raw: str) -> date | None:
    """Parse DD/MM/YYYY → date."""
    raw = raw.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _parse_row(row: list[str]) -> Transaction | None:
    """Parse a data row into a Transaction. Returns None if invalid."""
    if len(row) < 4:
        return None

    raw_date, note, raw_amount, category = row[0], row[1], row[2], row[3]

    if not raw_date or not raw_amount or not note or not category:
        return None

    parsed_date = _parse_date(raw_date)
    if parsed_date is None:
        return None

    try:
        amount = _parse_amount(raw_amount)
    except ValueError:
        return None

    try:
        return Transaction(
            date=parsed_date,
            amount=amount,
            note=note.strip(),
            category=category.strip(),
        )
    except ValidationError:
        return None


def sync_sheet(db_path: Path | None = None, only_month: str | None = None) -> SyncResult:
    """Sync new-format monthly sheets from Google Sheets into SQLite.

    Args:
        only_month: If set (MM/YYYY), sync only that sheet. Otherwise sync all.
    """
    db_path = db_path or Path(settings.db_path)
    init_db(db_path)

    logger.info("Connecting to Google Sheets...")
    gc = gspread.service_account(filename=settings.google_credentials_path)
    spreadsheet = gc.open_by_key(settings.google_sheet_id)

    result = SyncResult()

    for worksheet in spreadsheet.worksheets():
        sheet_name = worksheet.title

        if not _MONTHLY_SHEET_RE.match(sheet_name):
            logger.debug("Skipping non-monthly sheet: %s", sheet_name)
            continue

        if only_month and sheet_name != only_month:
            continue

        rows = worksheet.get_all_values()
        if not rows:
            continue

        if not _is_new_format(rows[0]):
            logger.info("Skipping old-format sheet: %s", sheet_name)
            continue

        data_rows = rows[1:]  # skip header
        logger.info("Syncing %s (%d data rows)", sheet_name, len(data_rows))

        for row in data_rows:
            tx = _parse_row(row)
            if tx is None:
                result.skipped += 1
                continue

            if insert_transaction(tx, sheet=sheet_name, db_path=db_path):
                result.imported += 1
            else:
                result.skipped += 1  # duplicate

    logger.info(
        "Sync done — imported: %d, skipped: %d, failed: %d",
        result.imported,
        result.skipped,
        result.failed,
    )
    return result
