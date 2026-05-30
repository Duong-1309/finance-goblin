# Future Roadmap

Ideas for future development, organized by category and effort level.

---

## 🔧 Hardware

### H-001: OLED 1.3" I2C Upgrade *(in progress — waiting for chip)*

Replace the LCD1602 serial stub with a real OLED 1.3" I2C display (SH1106/SSD1306, 128×64px).

**Why:** More display space enables richer UI — budget progress bar, icons, multi-line layout. Current 16×2 LCD limits message creativity.

**What changes:**
- `lcd_renderer.h` — implement real driver with U8g2 library
- Add budget progress bar (e.g. `█████░░ 72%`)
- Show date/time on idle screen

---

### H-002: Rotary Encoder

Add a physical rotary encoder (knob + push button) to navigate between display "screens".

**Why:** Touch-free interaction. User can browse different views without touching keyboard.

**Screens to cycle through:**
- Finance summary (current)
- Clock / date
- Weather (if backend fetches weather API)
- Top spending category this week

**What changes:**
- New `encoder_handler.h` in firmware
- `screen_manager.h` — cycle screens on rotate, confirm on press
- Backend: add `/api/weather` endpoint pulling from OpenWeatherMap (free tier)

---

### H-003: Receipt Photo Scanning

Point phone camera at a receipt → GPT Vision extracts merchant, amount, date, category → auto-log to Sheet + DB.

**Why:** Most expenses have a physical receipt. Eliminates manual typing for larger purchases.

**Flow:**
```
User sends photo to Telegram bot
→ GPT-4o vision: extract {merchant, amount, date, items}
→ Confirm with user (reply to message)
→ Append to Sheet + SQLite + MQTT push
```

**What changes:**
- `telegram_bot.py`: handle `message.photo` type
- `expense_parser.py`: add `parse_receipt_image(file_id)` using GPT-4o vision API
- Config: no new keys needed (same OpenAI key)

---

### H-004: Battery + Portable Mode

Add LiPo battery + TP4056 charging module. ESP32 goes to deep sleep when idle.

**Why:** Untethered desk companion — move it anywhere without USB cable. Wake on MQTT message.

**Behavior:**
- Deep sleep between polls (save power)
- Wake on MQTT message via ULP or light sleep
- Battery indicator on OLED (voltage reading via ADC)
- BLE push from phone when out of WiFi range

---

## 🤖 AI / Analysis

### A-001: Natural Language Query via Telegram

Ask questions about spending history in plain Vietnamese. GPT converts question to SQLite query, returns answer.

**Why:** Current `/report`, `/list`, `/top` commands are rigid. Natural language is more useful.

**Examples:**
```
"tháng trước tôi tiêu bao nhiêu cho cafe?"
→ SELECT SUM(amount) FROM transactions WHERE category='Ăn uống' AND note LIKE '%cafe%' AND date >= '2026-04-01'
→ "Bạn đã tiêu 320,000đ cho cafe tháng 4"

"3 tháng gần nhất tôi tiêu nhiều nhất vào mục gì?"
→ GROUP BY category, ORDER BY total DESC

"hôm nay tôi tiêu nhiều hơn hôm qua không?"
→ Compare daily totals
```

**What changes:**
- `telegram_bot.py`: new `/ask` command + fallback for questions (detect question intent)
- `app/services/nl_query.py`: GPT prompt → SQL → execute → format answer
- Security: only allow SELECT queries, no writes

---

### A-002: Spending Prediction

Predict end-of-month total based on current spending pace and historical patterns.

**Why:** Know in advance if you'll exceed budget — not just when you already did.

**Algorithm:**
- Days elapsed / days in month × current total = projected
- Adjust using same-period-last-month as baseline
- Risk upgrade: show "At this pace: 2.3M over budget" on OLED

**What changes:**
- `app/services/analyzer.py`: add `projected_monthly` field to `AnalysisResult`
- `app/services/state_builder.py`: use projection in message
- New LCD message template: `"Pace: +23% over"`

---

### A-003: Anomaly Detection

Alert when a single transaction is unusually large compared to category average.

**Why:** Catch mistakes (wrong amount entered) or unexpected large purchases early.

**Logic:**
- Per-category rolling average (last 30 days)
- If transaction > 3× average → anomaly alert
- Push via MQTT with `buzzer: alert`

**What changes:**
- `app/services/analyzer.py`: add anomaly check
- `app/services/telegram_bot.py`: send warning message back + MQTT push

**Example:**
```
Ăn uống average: 80k/transaction
New entry: "nhậu cuối năm 2,500,000"
→ ⚠️ MQTT push: "Big meal? 2.5M / 31x avg!"
```

---

### A-004: Monthly AI Report

Auto-generate a monthly summary at end of month, send as Telegram message (and optionally PDF).

**Why:** Monthly review is useful but no one manually runs `/report`. Automated delivery closes the loop.

**Content:**
- Total vs budget
- Category breakdown with % change vs previous month
- Biggest single transaction
- Goblin's one-line verdict on the month
- Trend: 3-month rolling comparison

**What changes:**
- `app/services/monthly_report.py`: aggregate data + GPT narrative
- Cron trigger: 1st of each month at 8am
- `telegram_bot.py`: `/monthlyreport [MM/YYYY]` manual trigger
- Optional: generate PDF (reuse GAS PDF logic or WeasyPrint)

---

## 📡 Integrations

### I-001: iOS Shortcuts / Android Tasker → `/api/notify`

Use phone automation tools to push any notification to the OLED without building a native app.

**Why:** Fastest way to get mobile events onto the display. No app development required.

**iOS Shortcuts examples:**
- Focus mode changed → push "Focus: Work"
- Calendar event in 15min → push event title
- Custom shortcut: tap → push custom text

**Android Tasker examples:**
- App notification received → HTTP POST to `/api/notify`
- Geofence exit → "Left office"

**Setup (no code changes needed — endpoint already exists):**
```
POST http://your-server:8000/api/notify
Headers: X-Device-Key: your-key
Body: {"line1": "Meeting soon", "line2": "10 mins", "mood": "warning"}
```

Only needs documentation + example Shortcut file.

---

### I-002: n8n / Make.com Webhook Integration

Connect external services (Gmail, Google Calendar, banking alerts) to the OLED via n8n automation.

**Why:** Hundreds of integrations without writing code. Gmail receipt → parse → push.

**Example flows:**
- Gmail label "Hoá đơn" → extract amount → log expense + push OLED
- Google Calendar event starts → push event name to OLED
- Vietcombank OTP SMS → parse transaction → log (if bank sends SMS)
- Weather alert → mood change on LED

**What changes:**
- Backend: document `/api/notify` webhook format clearly
- Add optional `duration` field — auto-revert display after N seconds
- Example n8n flow JSON in `docs/`

---

### I-003: Bank Statement CSV Import

Upload bank CSV export → parse → bulk import to SQLite.

**Why:** Most Vietnamese banks (VCB, TCB, MB) allow CSV export. Cover past transactions not manually logged.

**Supported formats:**
- Vietcombank CSV (common format)
- Generic: date, description, amount columns (user maps columns)

**What changes:**
- `telegram_bot.py`: handle `/import` command + document upload
- `app/services/csv_importer.py`: parse CSV, deduplicate, GPT-categorize
- Batch GPT call to categorize all rows at once (cheaper than one-by-one)

---

## 🖥️ UX / Product

### U-001: Web Dashboard

Simple web UI showing spending charts, category breakdown, budget progress.

**Why:** Telegram is great for input, but a visual dashboard makes data easier to review.

**Stack:** FastAPI + Jinja2 templates + Chart.js (no React, keep it simple)

**Pages:**
- `/` — this month overview: total, budget bar, category pie chart
- `/history` — month-by-month table
- `/settings` — set monthly budget, manage categories

**What changes:**
- `backend/app/api/dashboard.py` — HTML routes
- `backend/templates/` — Jinja2 HTML files
- `backend/static/` — Chart.js (CDN, no build step)
- Auth: same `X-Device-Key` header or simple HTTP Basic

---

### U-002: Budget Settings via Telegram

Set per-category budgets through the bot instead of editing `.env`.

**Why:** Budget should be adjustable without restarting the server.

**Commands:**
```
/setbudget 20000000          → set monthly total budget
/setbudget ăn uống 3000000   → set per-category limit
/budgets                     → show all current budgets
```

**What changes:**
- New `budgets` table in SQLite
- `app/services/analyzer.py`: use per-category budgets if set
- `telegram_bot.py`: handle `/setbudget` and `/budgets` commands

---

### U-003: Multi-Screen OLED Cycling

Automatically cycle between different information screens on the OLED.

**Why:** The display sits on a desk all day — show more than just finance.

**Screens:**
1. **Finance** (current) — AI message + budget state
2. **Clock** — time + date
3. **Weather** — temperature + condition (OpenWeatherMap free API)
4. **Daily summary** — today's total, transactions count

**Behavior:**
- Auto-cycle every 30s on idle
- MQTT event interrupts cycle and shows for 10s, then returns
- Button press: manually advance to next screen

**What changes:**
- `firmware/src/screen_manager.h` — screen state machine
- Backend: add `/api/clock` and `/api/weather` endpoints (or embed in device state)

---

## ⚙️ Ops / Reliability

### O-001: Automated SQLite Backup

Daily backup of `goblin.db` to Google Drive.

**Why:** SQLite is single-file — if server crashes and Docker volume is lost, all history is gone.

**What changes:**
- `app/services/backup.py`: compress DB + upload via Google Drive API
- Cron: daily at 2am
- Config: `BACKUP_GOOGLE_FOLDER_ID`

---

### O-002: Multi-User / Family Finance

Each family member has their own Telegram chat ID, expenses tracked separately, shared dashboard.

**Why:** Natural extension — household finance tracking, not just personal.

**Data model change:**
- Add `user_id` column to `transactions`
- Each Telegram user gets their own budget config
- Shared `/report` shows household total + per-person breakdown

---

## Priority Matrix

| | Low Effort | High Effort |
|---|---|---|
| **High Impact** | A-001 Natural language query | U-001 Web dashboard |
| | I-001 iOS Shortcuts doc | A-002 Spending prediction |
| | U-002 Budget via Telegram | I-003 Bank CSV import |
| | A-004 Monthly report | H-003 Receipt scanning |
| **Medium Impact** | A-003 Anomaly detection | O-002 Multi-user |
| | I-002 n8n integration | H-002 Rotary encoder |
| | O-001 DB backup | U-003 Multi-screen |
