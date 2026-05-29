# System Architecture

## High-Level Flow

```txt
Google Sheet
   |
Sync Worker
   |
Expense Analyzer
   |
Message Engine
   |
Device State API
   |
ESP32 Device
   |
LCD + LED + Buzzer
```

## Runtime Components

### Backend

Responsibilities:

- expose device API
- sync expense data
- analyze financial state
- generate device messages
- store transactions, insights, and logs

### Firmware

Responsibilities:

- connect to WiFi
- call backend API
- parse device state JSON
- render LCD messages
- control LED mood
- control buzzer alerts
- handle button input

### Data Source

The MVP data source is Google Sheet. Later versions can add bank exports, manual entry, calendar events, GitHub status, server health, and other personal context signals.

## Suggested Tech Stack

Backend:

- FastAPI
- SQLite
- APScheduler
- Docker later

Firmware:

- ESP32
- PlatformIO
- Arduino framework

AI:

- OpenAI API
- rule-based fallback messages

Frontend, future:

- Next.js
- Tailwind CSS
