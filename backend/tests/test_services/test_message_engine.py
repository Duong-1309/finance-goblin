from app.services.analyzer import AnalysisResult
from app.services.message_engine import generate_message


def make_result(**kwargs) -> AnalysisResult:
    base = dict(
        daily_total=0, weekly_total=0, monthly_total=5_000_000,
        top_category="An uong", top_category_amount=5_000_000,
        budget_usage_pct=25.0, risk_level="low",
    )
    base.update(kwargs)
    return AnalysisResult(**base)


def test_lines_max_16_chars() -> None:
    for risk in ("low", "medium", "high"):
        for _ in range(20):  # test multiple random picks
            msg = generate_message(make_result(risk_level=risk, budget_usage_pct=80))
            assert len(msg.line1) <= 16, f"line1 too long: {msg.line1!r}"
            assert len(msg.line2) <= 16, f"line2 too long: {msg.line2!r}"


def test_returns_two_lines() -> None:
    msg = generate_message(make_result())
    assert msg.line1
    assert msg.line2


def test_empty_data() -> None:
    msg = generate_message(make_result(monthly_total=0, budget_usage_pct=0))
    assert len(msg.line1) <= 16
    assert len(msg.line2) <= 16
