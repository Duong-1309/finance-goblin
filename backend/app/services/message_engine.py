import random
from dataclasses import dataclass

from app.services.analyzer import AnalysisResult

# LCD: max 16 chars per line, ASCII-safe Vietnamese removed
_TEMPLATES: dict[str, list[tuple[str, str]]] = {
    "high": [
        ("Budget {pct}%!", "{cat} eating u"),
        ("Broke? {pct}%!", "Cut {cat} NOW"),
        ("Wallet crying", "{pct}% gone..."),
        ("STOP SPENDING!", "{month} = {amt}"),
    ],
    "medium": [
        ("Spent {amt}", "{cat} is top"),
        ("{pct}% budget", "Watch {cat}"),
        ("Half gone", "{amt} this mo"),
        ("Easy there...", "{amt} spent"),
    ],
    "low": [
        ("All good! {pct}%", "Spent {amt}"),
        ("Goblin happy", "{amt} so far"),
        ("Nice & easy", "{cat} leading"),
        ("Budget ok", "{pct}% used"),
    ],
    "empty": [
        ("No data yet", "Add expenses"),
        ("Feed me data!", "No txn found"),
    ],
}


@dataclass
class MessageResult:
    line1: str
    line2: str


def _fmt(amount: float) -> str:
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f}tr"
    return f"{int(amount / 1_000)}k"


def _render(template: str, result: AnalysisResult) -> str:
    cat_short = result.top_category[:8] if result.top_category != "—" else "misc"
    return template.format(
        pct=f"{result.budget_usage_pct:.0f}",
        amt=_fmt(result.monthly_total),
        cat=cat_short,
        month=_fmt(result.monthly_total),
    )[:16]


def generate_message(result: AnalysisResult) -> MessageResult:
    if result.monthly_total == 0:
        templates = _TEMPLATES["empty"]
    else:
        templates = _TEMPLATES[result.risk_level]

    line1_tmpl, line2_tmpl = random.choice(templates)
    return MessageResult(
        line1=_render(line1_tmpl, result),
        line2=_render(line2_tmpl, result),
    )
