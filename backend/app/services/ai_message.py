import json
import logging
import time

from openai import OpenAI

from app.core.config import settings
from app.services.analyzer import AnalysisResult
from app.services.message_engine import MessageResult, generate_message

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a sarcastic desk goblin displayed on a 16-character LCD. "
    'Respond ONLY with JSON: {"line1": "...", "line2": "..."}. '
    "Rules: max 16 ASCII chars per line, no emojis, no Vietnamese, funny goblin tone."
)

_USER = (
    "Monthly spent: {monthly}\n"
    "Budget usage: {pct:.0f}%\n"
    "Top category: {cat}\n"
    "Risk level: {risk}\n"
    "Generate 2 LCD lines."
)

_CACHE_TTL_S = 600  # regenerate every 10 minutes max

# Cache: keyed by (risk_level, monthly_total_rounded, top_category)
_cache: dict[tuple, tuple[MessageResult, float]] = {}


def _cache_key(result: AnalysisResult) -> tuple:
    return (
        result.risk_level,
        round(result.monthly_total, -4),  # round to nearest 10k
        result.top_category,
    )


def generate_ai_message(result: AnalysisResult) -> MessageResult:
    """Generate AI message via GPT with caching. Falls back to rule-based on error."""
    if not settings.openai_api_key:
        return generate_message(result)

    key = _cache_key(result)
    cached_msg, cached_at = _cache.get(key, (None, 0.0))
    if cached_msg and (time.time() - cached_at) < _CACHE_TTL_S:
        logger.debug("AI message cache hit")
        return cached_msg

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM},
                {
                    "role": "user",
                    "content": _USER.format(
                        monthly=f"{result.monthly_total / 1_000_000:.1f}M VND",
                        pct=result.budget_usage_pct,
                        cat=result.top_category,
                        risk=result.risk_level,
                    ),
                },
            ],
            temperature=0.9,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        line1 = str(data.get("line1", ""))[:16]
        line2 = str(data.get("line2", ""))[:16]

        if not line1 or not line2:
            raise ValueError("empty lines from GPT")

        msg = MessageResult(line1=line1, line2=line2)
        _cache[key] = (msg, time.time())
        logger.info("GPT message (fresh): %r / %r", line1, line2)
        return msg

    except Exception as e:
        logger.warning("GPT message failed, using fallback: %s", e)
        return generate_message(result)


# Categories that are fixed/necessary — goblin is understanding, warm
_ESSENTIAL_CATEGORIES = {
    "Nhà ở",
    "Hoá đơn",
    "Người thân",
    "Học phí",
    "Sức khoẻ",
    "Nhà cửa",
    "Đầu tư",
}

# Categories that are discretionary — goblin is sarcastic and harsh
_SPLURGE_CATEGORIES = {
    "Ăn uống",
    "Chợ - Siêu thị",
    "Mua sắm",
    "Giải trí",
    "Làm đẹp",
}

_EXPENSE_SYSTEM_ESSENTIAL = (
    "You are a gentle, understanding goblin on a 16-char LCD. "
    'Respond ONLY with JSON: {"line1": "...", "line2": "..."}. '
    "Rules: max 16 ASCII chars per line, no emojis, warm and supportive tone, "
    "acknowledge this is a necessary expense."
)

_EXPENSE_SYSTEM_SPLURGE = (
    "You are a brutally sarcastic goblin on a 16-char LCD. "
    'Respond ONLY with JSON: {"line1": "...", "line2": "..."}. '
    "Rules: max 16 ASCII chars per line, no emojis, roast this wasteful purchase hard, "
    "reference the item specifically."
)

_EXPENSE_SYSTEM_NEUTRAL = (
    "You are a mildly sarcastic goblin on a 16-char LCD. "
    'Respond ONLY with JSON: {"line1": "...", "line2": "..."}. '
    "Rules: max 16 ASCII chars per line, no emojis, casual comment on the expense."
)

_EXPENSE_USER = (
    "Spent: {amount} on '{desc}' ({cat})\n"
    "Month total: {monthly} ({pct:.0f}% of budget)\n"
    "Risk: {risk}\n"
    "Write 2 LCD lines in your persona."
)


def generate_expense_event_message(
    description: str,
    amount: float,
    category: str,
    result: AnalysisResult,
) -> MessageResult:
    """Generate a contextual message for a just-logged expense. No cache — always fresh."""
    if not settings.openai_api_key:
        return generate_message(result)

    def _fmt(n: float) -> str:
        return f"{n / 1_000_000:.1f}M" if n >= 1_000_000 else f"{int(n / 1_000)}k"

    if category in _ESSENTIAL_CATEGORIES:
        system_prompt = _EXPENSE_SYSTEM_ESSENTIAL
    elif category in _SPLURGE_CATEGORIES:
        system_prompt = _EXPENSE_SYSTEM_SPLURGE
    else:
        system_prompt = _EXPENSE_SYSTEM_NEUTRAL

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": _EXPENSE_USER.format(
                        amount=_fmt(amount),
                        desc=description[:20],
                        cat=category,
                        monthly=_fmt(result.monthly_total),
                        pct=result.budget_usage_pct,
                        risk=result.risk_level,
                    ),
                },
            ],
            temperature=1.0,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        line1 = str(data.get("line1", ""))[:16]
        line2 = str(data.get("line2", ""))[:16]

        if not line1 or not line2:
            raise ValueError("empty lines")

        logger.info("Expense event msg: %r / %r", line1, line2)
        return MessageResult(line1=line1, line2=line2)

    except Exception as e:
        logger.warning("Expense event msg failed: %s", e)
        return generate_message(result)
