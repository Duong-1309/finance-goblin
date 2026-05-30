import logging
import re
from datetime import datetime
from pathlib import Path

import telebot

from app.core.categories import CATEGORIES
from app.core.config import settings
from app.db.allocation_repo import (
    clear_allocations,
    delete_allocation,
    get_allocation_total,
    get_allocations,
    set_allocation,
)
from app.db.database import get_connection, init_db
from app.db.income_repo import add_income, get_month_income, get_month_total
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

_MONTHLY_RE = re.compile(r"^\d{4}-\d{2}$")

bot = telebot.TeleBot(settings.telegram_token)

DB_PATH = Path(settings.db_path)
ALLOWED_CHAT_ID = settings.telegram_chat_id


def fmt_vnd(amount: float) -> str:
    return f"{amount:,.0f}đ".replace(",", ".")


_CAT_LOWER: dict[str, str] = {c.lower(): c for c in CATEGORIES}


def _normalize_category(raw: str) -> str:
    """Match user input to canonical category name (case-insensitive). Returns raw if no match."""
    return _CAT_LOWER.get(raw.strip().lower(), raw.strip())


def _parse_amount(raw: str) -> float | None:
    """Parse '3tr', '500k', '20000000' → float. Returns None if invalid."""
    raw = raw.strip().lower().replace(",", "")
    try:
        if raw.endswith("tr"):
            return float(raw[:-2]) * 1_000_000
        if raw.endswith("triệu"):
            return float(raw[:-5]) * 1_000_000
        if raw.endswith("k"):
            return float(raw[:-1]) * 1_000
        return float(raw)
    except ValueError:
        return None


def _guard(message: telebot.types.Message) -> bool:
    """Block anyone who isn't the owner."""
    if str(message.chat.id) != ALLOWED_CHAT_ID:
        bot.reply_to(message, "🤖 Không có quyền truy cập.")
        return False
    return True


def _current_month() -> str:
    return datetime.now().strftime("%Y-%m")


def _get_month_transactions(month_str: str) -> list[dict]:
    """Return all transactions for YYYY-MM month string."""
    if not month_str:
        month_str = _current_month()
    # Accept both YYYY-MM and legacy MM/YYYY
    if "/" in month_str:
        m, y = month_str.split("/")
        prefix = f"{y}-{m}"
    else:
        prefix = month_str  # YYYY-MM already

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
            "/plan                    – kế hoạch zero-based\n"
            "/income [số] [nguồn]     – log thu nhập\n"
            "/allocate [dm] [số]      – phân bổ bucket\n"
            "/report [YYYY-MM]        – tổng hợp tháng\n"
            "/budgets                 – xem budget + spending\n"
            "/list [YYYY-MM]          – danh sách\n"
            "/top [YYYY-MM]           – top 10\n"
            "/day [YYYY-MM-DD]        – theo ngày\n"
            "/sync                    – sync Sheet → DB"
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


@bot.message_handler(commands=["resync"])
def cmd_resync(message: telebot.types.Message) -> None:
    """Resync month from Google Sheet. Default: current month. /resync all for everything."""
    if not _guard(message):
        return
    arg = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else ""

    if arg == "all":
        bot.reply_to(message, "⏳ Resync toàn bộ...")
        with get_connection(DB_PATH) as conn:
            conn.execute("DELETE FROM transactions")
        result = sync_sheet(DB_PATH)
        label = "toàn bộ"
    else:
        # Default to current month if no arg
        month = arg if arg else _current_month()
        if not _MONTHLY_RE.match(month):
            bot.reply_to(message, "❌ Dùng YYYY-MM. VD: /resync 2026-05\n/resync all")
            return
        bot.reply_to(message, f"⏳ Resync tháng {month}...")
        with get_connection(DB_PATH) as conn:
            conn.execute("DELETE FROM transactions WHERE date LIKE ?", (f"{month}%",))
        y, m = month.split("-")
        result = sync_sheet(DB_PATH, only_month=f"{m}/{y}")
        label = f"tháng {month}"

    bot.reply_to(
        message,
        f"✅ Resync {label} xong\nImported: <b>{result.imported}</b>\nSkipped: {result.skipped}",
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

    # Use allocations as budget
    allocs = get_allocations(month_str, DB_PATH)
    alloc_total = sum(allocs.values())

    if alloc_total > 0:
        pct = total / alloc_total * 100
        msg = (
            f"💰 <b>Tháng {month_str}</b>: {fmt_vnd(total)} / {fmt_vnd(alloc_total)}\n"
            f"{_budget_emoji(pct)} {_budget_bar(pct)} {pct:.0f}%\n──────────────────────\n"
        )
    else:
        msg = f"💰 <b>Tổng chi tháng {month_str}</b>: {fmt_vnd(total)}\n──────────────────────\n"

    for cat, val in sorted(by_cat.items(), key=lambda x: -x[1]):
        alloc = allocs.get(cat, 0.0)
        if alloc > 0:
            cat_pct = val / alloc * 100
            e = _budget_emoji(cat_pct)
            msg += f"{e} {cat:<16s} {fmt_vnd(val)}/{fmt_vnd(alloc)} {cat_pct:.0f}%\n"
        else:
            share = val / total * 100
            msg += f"   {cat:<18s} {share:.1f}% – {fmt_vnd(val)}\n"

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
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", arg):
            bot.reply_to(message, "❌ Dùng định dạng YYYY-MM-DD. VD: /day 2026-05-16")
            return
        day_iso = arg
    else:
        day_iso = datetime.now().strftime("%Y-%m-%d")

    with get_connection(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT date, note, amount, category FROM transactions WHERE date = ? ORDER BY rowid",
            (day_iso,),
        ).fetchall()

    if not rows:
        bot.reply_to(message, f"❌ Không có dữ liệu ngày {day_iso}")
        return

    msg = f"📅 Chi tiêu ngày {day_iso}\n──────────────────────\n"
    for r in rows:
        msg += f"{r['note']} – {fmt_vnd(r['amount'])} – {r['category']}\n"
    total = sum(r["amount"] for r in rows)
    msg += f"──────────────────────\nTổng: {fmt_vnd(total)}"
    bot.reply_to(message, msg)


@bot.message_handler(commands=["setbudget"])
def cmd_setbudget(message: telebot.types.Message) -> None:
    """Alias for /allocate — redirects with hint."""
    if not _guard(message):
        return
    bot.reply_to(
        message,
        "💡 Dùng <b>/allocate</b> thay cho /setbudget:\n"
        "/allocate ăn uống 5tr\n"
        "/allocate tiết kiệm 15tr\n\n"
        "Allocate phân bổ theo tháng và drive toàn bộ hệ thống.",
        parse_mode="HTML",
    )


def _budget_bar(pct: float, width: int = 8) -> str:
    filled = min(int(pct / 100 * width), width)
    return "█" * filled + "░" * (width - filled)


def _budget_emoji(pct: float) -> str:
    if pct >= 100:
        return "🔴"
    if pct >= 80:
        return "⚠️"
    return "✅"


@bot.message_handler(commands=["budgets"])
def cmd_budgets(message: telebot.types.Message) -> None:
    """Show allocations vs actual spending — compact version of /plan."""
    if not _guard(message):
        return

    month = _current_month()
    allocations = get_allocations(month, DB_PATH)
    result = analyze(DB_PATH)

    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    with get_connection(DB_PATH) as conn:
        cat_rows = conn.execute(
            "SELECT category, SUM(amount) as spent FROM transactions"
            " WHERE date >= ? GROUP BY category",
            (month_start,),
        ).fetchall()
    cat_spent: dict[str, float] = {r["category"]: float(r["spent"]) for r in cat_rows}

    alloc_total = sum(allocations.values())
    msg = f"💰 <b>Tháng {month}</b>\n──────────────────────\n"

    if alloc_total > 0:
        pct = result.budget_usage_pct
        msg += (
            f"{_budget_emoji(pct)} Tổng: {fmt_vnd(result.monthly_total)}"
            f" / {fmt_vnd(alloc_total)}  {pct:.0f}%\n\n"
        )
    else:
        msg += f"Tổng: <b>{fmt_vnd(result.monthly_total)}</b>\n\n"

    all_cats = sorted(set(allocations) | set(cat_spent))
    for cat in all_cats:
        alloc = allocations.get(cat, 0.0)
        spent = cat_spent.get(cat, 0.0)
        if alloc > 0:
            pct = spent / alloc * 100
            msg += (
                f"{_budget_emoji(pct)} {cat}\n"
                f"   {fmt_vnd(spent)} / {fmt_vnd(alloc)}  {_budget_bar(pct, 6)} {pct:.0f}%\n"
            )
        else:
            msg += f"  · {cat:<18s} {fmt_vnd(spent)}\n"

    if not cat_spent:
        msg += "<i>Chưa có chi tiêu tháng này.</i>\n"

    msg += "\n<i>/allocate [danh mục] [số tiền] · /plan để xem đầy đủ</i>"
    bot.reply_to(message, msg, parse_mode="HTML")


@bot.message_handler(commands=["income"])
def cmd_income(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    arg = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else ""

    if not arg:
        # Show this month's income
        month = _current_month()
        rows = get_month_income(month, DB_PATH)
        total = get_month_total(month, DB_PATH)
        if not rows:
            bot.reply_to(message, f"Chưa có thu nhập tháng {month}.\n/income [số tiền] [nguồn]")
            return
        msg = f"💵 <b>Thu nhập tháng {month}</b>\n──────────────────────\n"
        for r in rows:
            msg += f"  {r['date']}  {fmt_vnd(r['amount'])}  {r['source']}\n"
        msg += f"──────────────────────\nTổng: <b>{fmt_vnd(total)}</b>"
        bot.reply_to(message, msg, parse_mode="HTML")
        return

    # /income 50tr lương [ghi chú]
    parts = arg.split(maxsplit=1)
    amount = _parse_amount(parts[0])
    if not amount:
        bot.reply_to(message, "❌ VD: /income 50tr lương\n/income 5tr thưởng dự án")
        return
    source = parts[1].strip() if len(parts) > 1 else "Thu nhập"
    add_income(amount=amount, source=source, db_path=DB_PATH)
    bot.reply_to(
        message,
        f"✅ Thu nhập: <b>{fmt_vnd(amount)}</b> – {source}",
        parse_mode="HTML",
    )


@bot.message_handler(commands=["allocate"])
def cmd_allocate(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    arg = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else ""
    if not arg:
        bot.reply_to(message, "❌ VD: /allocate ăn uống 5tr\n/allocate tiết kiệm 15tr")
        return

    parts = arg.rsplit(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ VD: /allocate ăn uống 5tr")
        return

    category = _normalize_category(parts[0])
    raw_amount = parts[1]
    amount = _parse_amount(raw_amount)
    if not amount:
        bot.reply_to(message, "❌ Không hiểu số tiền. VD: /allocate ăn uống 5tr")
        return

    month = _current_month()
    set_allocation(month, category, amount, DB_PATH)

    # Show unallocated remaining
    income_total = get_month_total(month, DB_PATH)
    alloc_total = get_allocation_total(month, DB_PATH)
    unallocated = income_total - alloc_total

    msg = f"✅ Phân bổ <b>{category}</b>: {fmt_vnd(amount)}\n"
    if income_total > 0:
        msg += f"📊 Đã phân bổ: {fmt_vnd(alloc_total)} / {fmt_vnd(income_total)}\n"
        if unallocated > 0:
            msg += f"⚠️ Chưa phân bổ: <b>{fmt_vnd(unallocated)}</b>"
        elif unallocated == 0:
            msg += "✅ Đã phân bổ hết — zero-based!"
        else:
            msg += f"🔴 Vượt thu nhập: {fmt_vnd(abs(unallocated))}"
    bot.reply_to(message, msg, parse_mode="HTML")


@bot.message_handler(commands=["clearalloc"])
def cmd_clearalloc(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    arg = message.text.split(maxsplit=1)[1].strip() if len(message.text.split()) > 1 else ""
    month = _current_month()

    if not arg:
        # Clear all allocations for this month
        n = clear_allocations(month, DB_PATH)
        bot.reply_to(message, f"🗑 Đã xóa {n} allocations tháng {month}.")
        return

    category = _normalize_category(arg)
    deleted = delete_allocation(month, category, DB_PATH)
    if deleted:
        bot.reply_to(message, f"🗑 Đã xóa allocation: <b>{category}</b>", parse_mode="HTML")
    else:
        bot.reply_to(message, f"❌ Không tìm thấy allocation: {category}")


@bot.message_handler(commands=["plan"])
def cmd_plan(message: telebot.types.Message) -> None:
    if not _guard(message):
        return
    month = _current_month()

    income_rows = get_month_income(month, DB_PATH)
    income_total = get_month_total(month, DB_PATH)
    allocations = get_allocations(month, DB_PATH)
    alloc_total = sum(allocations.values())

    # Actual spending per category this month
    month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    with get_connection(DB_PATH) as conn:
        cat_rows = conn.execute(
            "SELECT category, SUM(amount) as spent FROM transactions"
            " WHERE date >= ? GROUP BY category",
            (month_start,),
        ).fetchall()
    cat_spent: dict[str, float] = {r["category"]: float(r["spent"]) for r in cat_rows}
    total_spent = sum(cat_spent.values())

    msg = f"📊 <b>Kế hoạch tháng {month}</b>\n──────────────────────\n"

    # Income section
    if income_total > 0:
        msg += f"💵 Thu nhập: <b>{fmt_vnd(income_total)}</b>\n"
        for r in income_rows:
            msg += f"   · {r['source']}: {fmt_vnd(r['amount'])}\n"
        msg += "\n"
    else:
        msg += "💵 Thu nhập: <i>chưa log</i>  /income [số tiền] [nguồn]\n\n"

    # Allocations vs actual — always show all categories with spending
    all_cats = sorted(set(allocations.keys()) | set(cat_spent.keys()))
    if all_cats:
        if alloc_total > 0:
            msg += f"📌 Phân bổ: {fmt_vnd(alloc_total)}\n"
        else:
            msg += "📌 Chi tiêu theo danh mục  <i>(chưa allocate)</i>\n"
        for cat in all_cats:
            alloc = allocations.get(cat, 0.0)
            spent = cat_spent.get(cat, 0.0)
            if alloc > 0:
                pct = spent / alloc * 100
                bar = _budget_bar(pct, 5)
                emoji = _budget_emoji(pct)
                msg += f"  {emoji} {cat:<16s} {fmt_vnd(spent)}/{fmt_vnd(alloc)} {bar}\n"
            else:
                msg += f"  · {cat:<16s} {fmt_vnd(spent)}\n"
        if not allocations:
            msg += "\n<i>/allocate [danh mục] [số tiền]</i>\n"
        msg += "\n"
    else:
        msg += "📌 Chưa có chi tiêu tháng này\n\n"

    # Summary
    msg += f"💸 Thực chi: <b>{fmt_vnd(total_spent)}</b>\n"
    if income_total > 0:
        saved = income_total - total_spent
        rate = saved / income_total * 100
        emoji = "💰" if rate >= 20 else ("⚠️" if rate >= 0 else "🔴")
        msg += f"{emoji} Còn lại: <b>{fmt_vnd(saved)}</b> ({rate:.0f}%)\n"
    if income_total > 0 and alloc_total > 0:
        unalloc = income_total - alloc_total
        if unalloc > 0:
            msg += f"\n⚠️ Chưa phân bổ: {fmt_vnd(unalloc)}"
        elif unalloc == 0:
            msg += "\n✅ Zero-based: phân bổ hết thu nhập!"

    bot.reply_to(message, msg, parse_mode="HTML")


@bot.message_handler(func=lambda m: True)
def handle_expense(message: telebot.types.Message) -> None:
    """Any non-command text → parse as expense and record."""
    if not _guard(message):
        return

    text = message.text.strip()

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


def _register_commands() -> None:
    bot.set_my_commands(
        [
            telebot.types.BotCommand("plan", "Kế hoạch zero-based tháng này"),
            telebot.types.BotCommand("income", "Log thu nhập: 50tr lương"),
            telebot.types.BotCommand("allocate", "Phân bổ bucket: ăn uống 5tr"),
            telebot.types.BotCommand("report", "Tổng hợp chi tiêu [YYYY-MM]"),
            telebot.types.BotCommand("budgets", "Xem budget + spending tháng này"),
            telebot.types.BotCommand("setbudget", "Set budget limit: ăn uống 3tr"),
            telebot.types.BotCommand("list", "Danh sách chi tiêu [YYYY-MM]"),
            telebot.types.BotCommand("top", "Top 10 chi tiêu lớn nhất"),
            telebot.types.BotCommand("day", "Chi tiêu theo ngày [YYYY-MM-DD]"),
            telebot.types.BotCommand("sync", "Sync mới từ Google Sheet → DB"),
            telebot.types.BotCommand("resync", "Resync tháng hiện tại (hoặc YYYY-MM / all)"),
            telebot.types.BotCommand("clearalloc", "Xóa allocation: [danh mục] hoặc tất cả"),
            telebot.types.BotCommand("help", "Hướng dẫn sử dụng"),
        ]
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
    try:
        _register_commands()
        logger.info("Commands registered")
    except Exception as e:
        logger.warning("Could not register commands: %s", e)
    time.sleep(2)
    bot.infinity_polling(logger_level=logging.WARNING)
