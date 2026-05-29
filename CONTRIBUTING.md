# Contributing to Finance Goblin

## Development Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env   # fill in credentials
pytest                # verify everything works
```

### Firmware

```bash
cd firmware
cp include/config.example.h include/config.h   # fill in WiFi + backend URL
pio run              # build
pio run --target upload && pio device monitor   # flash + monitor
```

## Project Structure

```
backend/app/
  api/          HTTP route handlers + response schemas
  services/     Business logic — keep side effects here, not in api/
  db/           SQLite access — raw queries, no ORM
  models/       Pydantic validation models
  core/         Config, logging, security

firmware/src/
  main.cpp           Entry point + fetch loop
  wifi_manager.h     WiFi connect + reconnect
  api_client.h       HTTP GET + JSON parse
  lcd_renderer.h     LCD1602 driver (stub or real)
  led_controller.h   RGB LED mood mapping
  buzzer_controller.h Buzzer patterns + cooldown
  button_handler.h   Debounced button + mute state
```

## Making Changes

1. Fork the repo and create a branch: `git checkout -b feat/your-feature`
2. Write tests for new backend behavior (`tests/`)
3. Run `pytest` and `ruff check backend/` before committing
4. Open a pull request with a clear description

## Code Style

- Python: [Black](https://black.readthedocs.io) formatting, [ruff](https://docs.astral.sh/ruff) linting
- Type hints required on all function signatures
- No secrets or personal data in code or tests

## Adding a New Expense Category

Edit `CATEGORIES` in `backend/app/services/gemini_parser.py` — the list is shared by both the Telegram bot parser and the Google Sheet validator.

## Hardware Variants

The RGB LED wiring (common cathode vs common anode) is controlled by `RGB_COMMON_CATHODE` in `firmware/include/config.h`. The LCD can be switched from serial stub to real hardware by implementing `firmware/src/lcd_renderer.h` with the LiquidCrystal library.

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include your hardware setup and serial monitor output if the issue is firmware-related.
