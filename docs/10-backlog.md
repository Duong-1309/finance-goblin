# Backlog

For implementation-ready work items with descriptions, dependencies, and acceptance criteria, use [Agent Task Breakdown](11-agent-tasks.md).

## Now

- Create `backend/` FastAPI project.
- Add `GET /api/health`.
- Add mock `GET /api/device/state`.
- Create `firmware/` PlatformIO project.
- Connect ESP32 to WiFi.
- Fetch backend state from ESP32.
- Render LCD lines.
- Map mood to RGB LED.

## Next

- Add buzzer patterns.
- Add button mute behavior.
- Add SQLite database.
- Add transaction model.
- Add Google Sheet sync.
- Add spending analyzer.
- Add rule-based messages.

## Later

- Add OpenAI message generation.
- Add API key authentication.
- Add scheduler.
- Add Docker.
- Add logs and diagnostics.
- Add OLED animations.
- Add servo movement.
- Add GitHub or server status integration.

## Questions To Decide

- Which exact ESP32 board is being used?
- Is the RGB LED common anode or common cathode?
- What is the LCD I2C address?
- What is the Google Sheet column format?
- Should backend run locally on laptop, Raspberry Pi, or cloud?
- Should firmware use Arduino framework or ESP-IDF?
