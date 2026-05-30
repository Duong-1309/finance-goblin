# Changelog

## [Unreleased]

### Added

**Zero-based budgeting**
- `/income` — log monthly income by source
- `/allocate` — assign income to category buckets (case-insensitive, normalized to canonical names)
- `/plan` — full zero-based dashboard: income → allocations → actual spending → savings rate
- `/clearalloc [category]` — delete one or all allocations for current month
- `budget_allocations` + `income` tables in SQLite
- Analyzer uses allocation total as monthly budget (fallback to settings default)

**Bot improvements**
- `/resync [YYYY-MM|all]` — resync by month (default: current month) or full reimport
- `/budgets` always shows spending categories even with no allocations
- `/setbudget` redirects to `/allocate` with explanation
- Removed "⏳ Đang xử lý..." message from expense handler
- Category normalization: user input matched case-insensitively to canonical list
- `NULL` category fallback → `"Khác"`

**Date format standardization**
- All commands use ISO format: `YYYY-MM-DD` for days, `YYYY-MM` for months
- `sheet_sync`: accepts both `DD/MM/YYYY` and `YYYY-MM-DD` date formats from Google Sheet

**Firmware**
- Passive buzzer melodies per mood (happy/warning/panic/offline/soft)
- `BUZZER_PASSIVE` flag in `config.h`
- Melody frequencies shifted to 1–3.5kHz for cheap buzzers

**Infrastructure**
- `app/core/categories.py` — single source of truth for category list
- MQTT: `mosquitto.conf`, Mosquitto in Docker Compose, `paho-mqtt` in backend
- `POST /api/notify` endpoint for external push to OLED

---


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
