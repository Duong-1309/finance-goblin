# Finance Goblin 🧌

[![Tests](https://github.com/YOUR_USERNAME/finance-goblin/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/finance-goblin/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![PlatformIO](https://img.shields.io/badge/firmware-PlatformIO-orange.svg)](https://platformio.org)

An ESP32 desk companion that turns your personal finance data into ambient physical feedback — LCD messages, RGB mood lighting, and buzzer alerts — driven by a sarcastic AI goblin personality.

```
Telegram → GPT-4o-mini → Google Sheets → FastAPI → ESP32 → LCD + LED + Buzzer
```

## Features

- **Log expenses** via Telegram in plain Vietnamese — GPT parses amount and category automatically
- **Ambient feedback** — RGB LED changes color based on monthly budget usage
- **Goblin personality** — AI-generated snarky 2-line messages on LCD1602
- **Google Sheets sync** — reads from your existing expense spreadsheet
- **Offline fallback** — ESP32 shows "Backend offline" and switches LED to white

## Hardware (MVP)

| Component | Where |
|---|---|
| ESP32 dev board | Main controller |
| LCD1602 (direct 6-wire) | Display |
| RGB LED module | Mood indicator |
| Active buzzer | Alerts |
| Push button | Mute buzzer |

Full wiring diagram: [docs/06-hardware-wiring.md](docs/06-hardware-wiring.md)

## Quick Start

### 1. Backend

```bash
cd backend
cp env.example .env          # fill in your credentials
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or with Docker:

```bash
cp backend/env.example backend/.env   # fill in your credentials
docker compose up -d
```

### 2. Telegram Bot

```bash
cd backend
python run_bot.py
```

Or via Docker (included in `docker compose up -d`).

### 3. Firmware

```bash
cd firmware
cp include/config.example.h include/config.h   # fill in WiFi + backend URL
pio run --target upload
pio device monitor
```

## Project Structure

```
backend/          FastAPI service + Telegram bot
  app/
    api/          HTTP endpoints
    services/     Business logic (analyzer, AI messages, sheet sync)
    db/           SQLite storage
    models/       Pydantic models
  tests/
firmware/         ESP32 PlatformIO project
  src/
    main.cpp
    wifi_manager.h
    api_client.h
    lcd_renderer.h
    led_controller.h
    buzzer_controller.h
    button_handler.h
docs/             Design documents
```

## Configuration

Copy `backend/env.example` to `backend/.env` and fill in:

| Variable | Description |
|---|---|
| `GOOGLE_SHEET_ID` | Your Google Sheets ID from the URL |
| `GOOGLE_CREDENTIALS_PATH` | Path to service account JSON |
| `TELEGRAM_TOKEN` | From @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram user ID |
| `OPENAI_API_KEY` | For AI-generated LCD messages |
| `MONTHLY_BUDGET` | Budget in VND (default: 20,000,000) |
| `DEVICE_API_KEY` | Secret shared with ESP32 (optional) |

See [docs/12-google-sheet-format.md](docs/12-google-sheet-format.md) for the expected Google Sheet structure.

## Telegram Bot Commands

| Command | Description |
|---|---|
| Any text | Log expense (e.g. `cơm trưa 50k`) |
| `/report [MM/YYYY]` | Monthly spending summary |
| `/list [MM/YYYY]` | All transactions |
| `/top [MM/YYYY]` | Top 10 by amount |
| `/day [DD/MM/YYYY]` | Spending for a specific day |
| `/sync` | Force sync Google Sheet → DB |

## LED Mood Colors

| Color | Mood | Trigger |
|---|---|---|
| 🟢 Green | Happy | < 50% budget used |
| 🟡 Yellow | Warning | 50–85% budget used |
| 🔴 Red | Panic | > 85% budget used |
| 🔵 Blue | Sleep | No data |
| ⚪ White | Offline | Backend unreachable |

## Development

```bash
cd backend
pip install -r requirements.txt
pytest                          # run all tests
pytest tests/test_api/          # single module
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Documentation

- [Project Overview](docs/00-project-overview.md)
- [System Architecture](docs/02-system-architecture.md)
- [Backend Design](docs/03-backend-design.md)
- [Firmware Design](docs/04-firmware-design.md)
- [API Specification](docs/05-api-specification.md)
- [Hardware Wiring](docs/06-hardware-wiring.md)

## License

MIT — see [LICENSE](LICENSE).
