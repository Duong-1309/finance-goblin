import logging
from datetime import datetime

import gspread

from app.core.config import settings

logger = logging.getLogger(__name__)


def append_spending(description: str, amount: float, category: str) -> str:
    """Append one expense row to the current month's sheet. Returns sheet name."""
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    sheet_name = now.strftime("%m/%Y")

    gc = gspread.service_account(filename=settings.google_credentials_path)
    spreadsheet = gc.open_by_key(settings.google_sheet_id)

    # Get or create this month's sheet
    try:
        ws = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=sheet_name, rows=500, cols=10)
        ws.append_row(["Thời gian", "Lý do", "Số tiền", "Danh mục"])
        logger.info("Created new sheet: %s", sheet_name)

    ws.append_row([date_str, description, amount, category])
    logger.info("Appended to %s: %s %.0f %s", sheet_name, description, amount, category)
    return sheet_name
