# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Finance Goblin is an ESP32-based desk companion that reads personal expense data from Google Sheets and renders ambient financial feedback via LCD text, RGB LED mood lighting, buzzer alerts, and AI-generated goblin personality messages.

**Current status:** Planning phase — no code exists yet. Start with the tasks in [docs/11-agent-tasks.md](docs/11-agent-tasks.md).

**System flow:** Google Sheet → FastAPI backend (Python) → ESP32 firmware (C++ / PlatformIO) → LCD1602 + RGB LED + Buzzer

---

## Repository Structure (planned)

```
backend/          # FastAPI Python service
  app/
    main.py
    api/          # Route handlers (health.py, device.py)
    core/         # Config, settings
  requirements.txt
firmware/         # ESP32 PlatformIO project
  platformio.ini
  src/main.cpp
  include/        # config.example.h (private config excluded from git)
docs/             # Design documents (read these before implementing)
```

---

## Commands

Once scaffolded, the backend runs as:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tests (once scaffolded):

```bash
cd backend
pytest
pytest tests/test_api/test_health.py  # single test file
```

Firmware (once scaffolded):

```bash
cd firmware
pio run              # build
pio run --target upload  # flash to ESP32
pio device monitor   # serial monitor
```

---

## API Contract

### `GET /api/health`

```json
{ "status": "ok" }
```

### `GET /api/device/state`

```json
{
  "line1": "Coffee +43%",
  "line2": "Goblin worried",
  "mood": "warning",
  "led": "yellow",
  "buzzer": "soft",
  "refresh_after": 60
}
```

**Enum constraints:**
- `mood`: `happy` | `warning` | `panic` | `sleep` | `offline`
- `led`: `green` | `yellow` | `red` | `blue` | `white`
- `buzzer`: `silent` | `soft` | `alert`
- `line1`, `line2`: max **16 ASCII characters** each

Authentication: `X-Device-Key` header required for `/api/device/state` (Milestone 4). `/api/health` stays public.

---

## Hardware Wiring

| Component | GPIO |
|-----------|------|
| LCD SDA | 21 |
| LCD SCL | 22 |
| RGB Red | 18 |
| RGB Green | 19 |
| RGB Blue | 23 |
| Button | 4 |
| Buzzer | 5 |

LED color → mood: green=happy, yellow=warning, red=panic, blue=sleep, white=offline

---

## Architecture Layers

**Backend:**
- `app/api/` — HTTP route handlers, response models
- `app/services/` — orchestration (sync scheduler, state builder)
- `app/analyzers/` — spending calculations (daily/weekly/monthly totals, risk level: `low`/`medium`/`high`)
- `app/ai/` — message generation (rule-based engine + optional AI API with fallback)
- `app/models/` — SQLite tables: `transactions`, `insights`, `generated_messages`

**Firmware:**
- WiFi manager → API client → JSON parser → LCD renderer + LED controller + Buzzer
- Fetch loop driven by `refresh_after` (default 60s if missing/invalid)
- Offline fallback: LCD shows `"Backend offline" / "Retrying..."`, LED turns white

---

## Implementation Task Order

Tasks are defined in [docs/11-agent-tasks.md](docs/11-agent-tasks.md). Suggested order:

**Milestone 1 (Device Alive):** BE-001 → BE-002 → BE-003 → BE-004 → FW-001 → FW-002 → FW-003 → FW-004 → FW-005 → FW-006

**Milestone 2 (Finance Brain):** DATA-001 → BE-005 → BE-006 → BE-007 → BE-008 → BE-009

**Milestone 3 (Personality):** BE-010 → BE-011 → FW-007 → FW-008

**Milestone 4 (Stable):** OPS-001 → OPS-002 → OPS-003 → SEC-001 → QA-001

---

## Working Rules

- Keep changes scoped to the task being implemented.
- `firmware/include/config.h` (private WiFi credentials, backend URL, API key) must be gitignored — only commit `config.example.h`.
- Backend `.env` is gitignored — only commit `.env.example`.
- Prefer simple working implementations over abstractions.
- Add backend tests when practical; use an isolated test database.
- Update docs when behavior or commands change.
- AI message generation is disabled by default; requires explicit env flag.
