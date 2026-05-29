# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-05-29

### Added

**Backend**
- FastAPI service with `/api/health` and `/api/device/state` endpoints
- SQLite storage for transactions, with duplicate detection
- Google Sheets sync (new-format sheets: `MM/YYYY`, 4-column layout)
- Spending analyzer: daily/weekly/monthly totals, top category, risk level
- GPT-4o-mini AI messages for LCD with 10-minute cache + rule-based fallback
- `X-Device-Key` header authentication for device endpoint
- Structured logging

**Telegram Bot**
- Expense logging via natural language (GPT-4o-mini parser)
- Commands: `/report`, `/list`, `/top`, `/day`, `/sync`
- Writes to Google Sheets and local SQLite in one step

**Firmware (ESP32)**
- WiFi connection with retry
- HTTP client for `/api/device/state` with offline fallback
- RGB LED mood mapping (green/yellow/red/blue/white)
- LCD1602 serial stub (real hardware driver pending)
- Buzzer patterns: silent / soft / alert with 5-minute cooldown
- Button mute with debounce
- Fetch loop driven by `refresh_after`

**Ops**
- Docker Compose for backend + bot
- `env.example` and `config.example.h` templates
