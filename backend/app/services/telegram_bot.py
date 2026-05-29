import logging
from datetime import datetime
from pathlib import Path

import telebot

from app.core.config import settings
from app.db.database import get_connection, init_db
from app.db.transaction_repo import insert_transaction
from app.models.transaction import Transaction
from app.services.ai_message import generate_expense_event_message
from app.services.analyzer import analyze
from app.services.expense_parser import parse_spending
from app.services.mqtt_publisher import publish_display
from app.services.sheet_sync import sync_sheet
from app.services.sheet_writer import append_spending
from app.services.state_builder import build_device_state

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(settings.telegram_token)

DB_PATH = Path(settings.db_path)
ALLOWED_CHAT_ID = settings.telegram_chat_id


def fmt_vnd(amount: float) -> str:
    return f"{amount:,.0f}đ".replace(",", ".")


def _guard(message: telebot.types.Message) -> bool:
    """Block anyone who isn't the owner."""
    if str(message.chat.id) != ALLOWED_CHAT_ID:
        bot.reply_to(message, "🤖 Không có quyền truy cập.")
        return False
    return True


def _current_month() -> str:
    return datetime.now().strftime("%m/%Y")


def _get_month_transactions(month_str: str) -> list[dict]:
    """Return all transactions for MM/YYYY month string."""
    if not month_str:
        month_str = _current_month()
    try:
        m, y = month_str.split("/")
        prefix = f"{y}-{m}"
    except ValueError:
        return []

    with get_connection(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT date, note, amount, category FROM transactions WHERE date LIKE ? ORDER BY date",
            (f"{prefix}%",),
        ).fetchall()
    return [dict(r) for r in rows]


# ─── HANDLERS ────────────────────────────────────────────


@bot.message_handler(commands=["start", "help"])
def cmd_help(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    bot.reply_to(
        message,
        (
            "🧌 <b>Finance Goblin</b>\n\n"
            "Gõ bất kỳ để ghi chi tiêu.\n\n"
            "<b>Lệnh:</b>\n"
            "/report [MM/YYYY] – tổng hợp tháng\n"
            "/list [MM/YYYY]   – danh sách\n"
            "/top [MM/YYYY]    – top 10 lớn nhất\n"
            "/day [DD/MM/YYYY] – chi tiêu theo ngày\n"
            "/sync             – sync Google Sheet → DB"
        ),
        parse_mode="HTML",
    )


@bot.message_handler(commands=["sync"])
def cmd_sync(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    bot.reply_to(message, "⏳ Đang sync...")
    result = sync_sheet(DB_PATH)
    bot.reply_to(
        message,
        f"✅ Sync xong\nImported: <b>{result.imported}</b>\nSkipped: {result.skipped}",
        parse_mode="HTML",
    )


@bot.message_handler(commands=["report"])
def cmd_report(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    arg = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else ""
    month_str = arg or _current_month()
    rows = _get_month_transactions(month_str)
    if not rows:
        bot.reply_to(message, f"❌ Không có dữ liệu tháng {month_str}")
        return

    total = sum(r["amount"] for r in rows)
    by_cat: dict[str, float] = {}
    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + r["amount"]

    msg = f"💰 <b>Tổng chi tháng {month_str}</b>: {fmt_vnd(total)}\n──────────────────────\n"
    for cat, val in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = val / total * 100
        msg += f"{cat:<20s} {pct:.1f}% – {fmt_vnd(val)}\n"
    bot.reply_to(message, msg, parse_mode="HTML")


@bot.message_handler(commands=["list"])
def cmd_list(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    arg = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else ""
    month_str = arg or _current_month()
    rows = _get_month_transactions(month_str)
    if not rows:
        bot.reply_to(message, f"❌ Không có dữ liệu tháng {month_str}")
        return

    msg = f"📋 Chi tiêu tháng {month_str}\n──────────────────────\n"
    for r in rows:
        msg += f"{r['date']} – {r['note']} – {fmt_vnd(r['amount'])} – {r['category']}\n"
    bot.reply_to(message, msg)


@bot.message_handler(commands=["top"])
def cmd_top(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    parts = message.text.split(maxsplit=1)[1].split(",") if len(message.text.split()) > 1 else []
    month_str = parts[0].strip() if parts else _current_month()
    n = int(parts[1].strip()) if len(parts) > 1 else 10

    rows = sorted(_get_month_transactions(month_str), key=lambda r: -r["amount"])[:n]
    if not rows:
        bot.reply_to(message, f"❌ Không có dữ liệu tháng {month_str}")
        return

    msg = f"🏆 Top {n} chi tiêu tháng {month_str}\n──────────────────────\n"
    for r in rows:
        msg += f"{r['date']} – {r['note']} – {fmt_vnd(r['amount'])} – {r['category']}\n"
    bot.reply_to(message, msg)


@bot.message_handler(commands=["day"])
def cmd_day(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    arg = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else ""
    if arg:
        try:
            d, mo, y = arg.split("/")
            day_iso = f"{y}-{mo}-{d}"
            day_display = arg
        except ValueError:
            bot.reply_to(message, "❌ Dùng định dạng DD/MM/YYYY")
            return
    else:
        day_iso = datetime.now().strftime("%Y-%m-%d")
        day_display = datetime.now().strftime("%d/%m/%Y")

    with get_connection(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT date, note, amount, category FROM transactions WHERE date = ? ORDER BY rowid",
            (day_iso,),
        ).fetchall()

    if not rows:
        bot.reply_to(message, f"❌ Không có dữ liệu ngày {day_display}")
        return

    msg = f"📅 Chi tiêu ngày {day_display}\n──────────────────────\n"
    for r in rows:
        msg += f"{r['note']} – {fmt_vnd(r['amount'])} – {r['category']}\n"
    total = sum(r["amount"] for r in rows)
    msg += f"──────────────────────\nTổng: {fmt_vnd(total)}"
    bot.reply_to(message, msg)


@bot.message_handler(func=lambda m: True)
def handle_expense(message: telebot.types.Message) -> None:
    """Any non-command text → parse as expense and record."""
    if not _guard(message):
        return

    text = message.text.strip()
    bot.reply_to(message, "⏳ Đang xử lý...")

    parsed = parse_spending(text)
    description = parsed["description"]
    amount = float(parsed["amount"])
    category = str(parsed["category"])

    if amount <= 0:
        bot.reply_to(
            message,
            f"⚠️ Không parse được số tiền.\n"
            f"Mô tả: <b>{description}</b> – Danh mục: {category}\n"
            "Thử lại với format: <i>cơm trưa 50k ăn uống</i>",
            parse_mode="HTML",
        )
        return

    # 1. Write to Google Sheet
    sheet_name = append_spending(description, amount, category)

    # 2. Sync that sheet into SQLite
    try:
        tx = Transaction(
            date=datetime.now().date(),
            amount=amount,
            note=description,
            category=category,
        )
        insert_transaction(tx, sheet=sheet_name, db_path=DB_PATH)
    except Exception as e:
        logger.warning("Local DB insert failed: %s", e)

    # 3. Push contextual event message to OLED via MQTT
    try:
        result = analyze(DB_PATH)
        msg = generate_expense_event_message(description, amount, category, result)
        state = build_device_state(result)
        publish_display(state.model_copy(update={"line1": msg.line1, "line2": msg.line2}))
    except Exception as e:
        logger.warning("MQTT push failed: %s", e)

    bot.reply_to(
        message,
        f"✅ Đã ghi: <b>{description}</b>\n💰 {fmt_vnd(amount)} – {category}",
        parse_mode="HTML",
    )


def run() -> None:
    import time

    init_db(DB_PATH)
    logger.info("Finance Goblin bot starting...")
    # Clear any active webhook or conflicting session before polling
    try:
        bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook cleared")
    except Exception as e:
        logger.warning("Could not clear webhook: %s", e)
    time.sleep(2)
    bot.infinity_polling(logger_level=logging.WARNING)
