from app.api.schemas import Buzzer, Led, Mood
from app.services.analyzer import AnalysisResult
from app.services.state_builder import build_device_state


def make_result(**kwargs) -> AnalysisResult:
    base = dict(
        daily_total=0, weekly_total=0, monthly_total=5_000_000,
        top_category="Ăn uống", top_category_amount=5_000_000,
        budget_usage_pct=25.0, risk_level="low",
    )
    base.update(kwargs)
    return AnalysisResult(**base)


def test_low_risk_state() -> None:
    s = build_device_state(make_result(risk_level="low", budget_usage_pct=25))
    assert s.mood == Mood.happy
    assert s.led == Led.green
    assert s.buzzer == Buzzer.silent


def test_medium_risk_state() -> None:
    s = build_device_state(make_result(risk_level="medium", budget_usage_pct=70))
    assert s.mood == Mood.warning
    assert s.led == Led.yellow
    assert s.buzzer == Buzzer.soft


def test_high_risk_state() -> None:
    s = build_device_state(make_result(risk_level="high", budget_usage_pct=90))
    assert s.mood == Mood.panic
    assert s.led == Led.red
    assert s.buzzer == Buzzer.alert


def test_empty_state() -> None:
    s = build_device_state(make_result(monthly_total=0, budget_usage_pct=0))
    assert s.mood == Mood.sleep
    assert s.led == Led.blue


def test_lcd_lines_max_16_chars() -> None:
    s = build_device_state(make_result(
        risk_level="high", budget_usage_pct=92,
        top_category="Chợ - Siêu thị", monthly_total=18_500_000,
    ))
    assert len(s.line1) <= 16
    assert len(s.line2) <= 16
