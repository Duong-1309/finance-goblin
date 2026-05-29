# Agent Task Breakdown

This document breaks the project into small implementation tasks for coding agents. Each task should be treated as an independent unit of work unless dependencies are listed.

## Working Rules For Agents

- Keep changes scoped to the task.
- Update docs when behavior or commands change.
- Do not commit secrets, WiFi credentials, API keys, or Google credentials.
- Prefer simple working implementations over abstractions.
- Add tests for backend logic when practical.
- Keep firmware configuration in example files, not hardcoded private values.

## Milestone 1: Device Alive

Goal: create a working loop where an ESP32 can fetch mock state from a backend and render it through LCD and RGB LED.

### BE-001: Scaffold Backend Project

Description:

Create a minimal FastAPI backend under `backend/`. The backend should be runnable locally and ready for future modules.

Scope:

- Create `backend/` directory.
- Add FastAPI app entrypoint.
- Add dependency file.
- Add local run instructions.
- Add basic project structure for API routes and settings.

Suggested structure:

```txt
backend/
  app/
    __init__.py
    main.py
    api/
      __init__.py
      health.py
      device.py
    core/
      __init__.py
      config.py
  requirements.txt
  README.md
```

Acceptance Criteria:

- `backend/app/main.py` exposes a FastAPI app.
- Backend can be started with a documented command.
- Visiting `/docs` shows FastAPI Swagger UI.
- No secrets or local machine values are hardcoded.
- `backend/README.md` explains setup and run command.

Dependencies:

- None.

### BE-002: Add Health Endpoint

Description:

Add a backend health endpoint so the firmware and humans can verify that the service is running.

Endpoint:

```txt
GET /api/health
```

Expected response:

```json
{
  "status": "ok"
}
```

Acceptance Criteria:

- `GET /api/health` returns HTTP 200.
- Response body exactly includes `"status": "ok"`.
- Endpoint is visible in Swagger UI.
- A simple test covers the endpoint.

Dependencies:

- BE-001.

### BE-003: Add Mock Device State Endpoint

Description:

Add a mock endpoint that returns the current device display state. This will let firmware development proceed before Google Sheet and finance analysis exist.

Endpoint:

```txt
GET /api/device/state
```

Expected response:

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

Acceptance Criteria:

- `GET /api/device/state` returns HTTP 200.
- Response includes `line1`, `line2`, `mood`, `led`, `buzzer`, and `refresh_after`.
- `line1` and `line2` are no longer than 16 characters.
- `refresh_after` is a positive integer.
- A simple test covers the endpoint schema.

Dependencies:

- BE-001.

### BE-004: Add Device State Models

Description:

Add explicit response models for the device state API so future code has a stable contract.

Scope:

- Add a device state schema/model.
- Restrict mood values.
- Restrict LED values.
- Restrict buzzer values.
- Use the model in `/api/device/state`.

Allowed values:

```txt
mood: happy, warning, panic, sleep, offline
led: green, yellow, red, blue, white
buzzer: silent, soft, alert
```

Acceptance Criteria:

- Device state response is validated by a model.
- Invalid enum values are not accepted in code paths that construct state.
- Swagger UI shows the response schema.
- Tests verify valid mock state.

Dependencies:

- BE-003.

### FW-001: Scaffold Firmware Project

Description:

Create a PlatformIO firmware project under `firmware/` for ESP32 using the Arduino framework.

Scope:

- Create PlatformIO project files.
- Add initial `src/main.cpp`.
- Add config example for WiFi and backend URL.
- Add firmware README with build/upload instructions.

Suggested structure:

```txt
firmware/
  platformio.ini
  src/
    main.cpp
  include/
    config.example.h
  README.md
```

Acceptance Criteria:

- PlatformIO project is present under `firmware/`.
- Firmware builds successfully for an ESP32 board.
- Private WiFi credentials are not committed.
- `firmware/README.md` explains how to create local config.

Dependencies:

- None.

### FW-002: Implement WiFi Connection

Description:

Connect ESP32 to WiFi and expose connection status over serial logs.

Scope:

- Read WiFi SSID/password from local config.
- Connect on boot.
- Retry connection if initial connection fails.
- Print useful status to serial monitor.

Acceptance Criteria:

- Firmware attempts WiFi connection on boot.
- Serial monitor shows connection progress.
- Serial monitor shows local IP after successful connection.
- WiFi credentials are loaded from local ignored config.
- Failed connection does not crash the device.

Dependencies:

- FW-001.

### FW-003: Implement Backend API Client

Description:

Make ESP32 call the backend mock device state endpoint and parse the JSON response.

Scope:

- Add HTTP client call to `/api/device/state`.
- Parse JSON fields into a local device state struct.
- Handle timeout or non-200 responses.
- Log parsed state to serial.

Acceptance Criteria:

- ESP32 calls configured backend URL.
- Successful response is parsed into `line1`, `line2`, `mood`, `led`, `buzzer`, and `refresh_after`.
- Serial monitor prints parsed values.
- Failed request creates an offline fallback state.
- HTTP timeout is finite and documented.

Dependencies:

- FW-002.
- BE-003.

### FW-004: Render LCD1602 Text

Description:

Render backend-provided text on LCD1602.

Scope:

- Initialize LCD1602 over I2C.
- Render `line1` on row 0.
- Render `line2` on row 1.
- Truncate or pad lines to avoid display artifacts.
- Show offline text when backend is unavailable.

Acceptance Criteria:

- LCD initializes on boot.
- LCD shows two lines from `/api/device/state`.
- Lines longer than 16 characters are safely truncated.
- Old characters do not remain after shorter messages.
- Offline fallback displays readable text.

Dependencies:

- FW-003.

### FW-005: Implement RGB LED Mood Mapping

Description:

Map backend mood or LED value to physical RGB LED output.

Scope:

- Configure RGB GPIO pins.
- Implement color mapping.
- Support common cathode or clearly document current assumption.
- Set LED color after each successful device state fetch.
- Set offline color when backend fails.

Color mapping:

```txt
green: happy
yellow: warning
red: panic
blue: sleep
white: offline
```

Acceptance Criteria:

- RGB pins are configured.
- LED changes color based on API response.
- Offline state sets LED to white.
- Color mapping is documented in firmware README.
- Code can be adjusted for common anode/cathode with one obvious setting or function.

Dependencies:

- FW-003.

### FW-006: Implement Fetch Loop

Description:

Make the device repeatedly fetch state from the backend using `refresh_after`.

Scope:

- Fetch state on boot after WiFi connects.
- Wait `refresh_after` seconds before next fetch.
- Use a safe default refresh interval if response is invalid.
- Avoid blocking WiFi reconnect forever.

Acceptance Criteria:

- Device refreshes state repeatedly.
- `refresh_after` controls the next fetch delay.
- Invalid or missing `refresh_after` falls back to 60 seconds.
- Device continues running after backend errors.
- Serial logs clearly show each fetch attempt.

Dependencies:

- FW-003.
- FW-004.
- FW-005.

## Milestone 2: Finance Brain

Goal: replace mock state with real expense analysis from Google Sheet data.

### DATA-001: Define Google Sheet Format

Description:

Document the exact Google Sheet columns that the backend expects.

Recommended columns:

```txt
date, amount, category, note, payment_method
```

Acceptance Criteria:

- A docs file describes the sheet format.
- Required and optional columns are identified.
- Example rows are included.
- Date format and currency assumptions are documented.
- Invalid row handling is described.

Dependencies:

- None.

### BE-005: Add Transaction Model

Description:

Add a transaction domain model for expense records.

Scope:

- Add transaction schema/model.
- Include date, amount, category, note, payment method.
- Add validation for positive amount.
- Add tests for valid and invalid transactions.

Acceptance Criteria:

- Transaction model exists in backend.
- Amount must be positive.
- Date is parsed consistently.
- Tests cover basic validation.

Dependencies:

- BE-001.
- DATA-001.

### BE-006: Add SQLite Storage

Description:

Add local SQLite storage for transactions, insights, and generated messages.

Scope:

- Configure SQLite database.
- Add database initialization.
- Add transaction table.
- Add generated messages table.
- Add insights table if practical.

Acceptance Criteria:

- Backend can create a local SQLite database.
- Transaction records can be inserted and queried.
- Database file path is configurable.
- Tests use an isolated test database.
- Local database files are ignored by git.

Dependencies:

- BE-005.

### BE-007: Implement Google Sheet Sync

Description:

Read expenses from Google Sheet and store them as transactions.

Scope:

- Add Google credentials configuration.
- Read rows from a configured sheet.
- Convert rows into transaction records.
- Skip or report invalid rows.
- Avoid duplicate imports.

Acceptance Criteria:

- Backend can sync transactions from Google Sheet.
- Sheet ID and range are configured through environment variables.
- Invalid rows do not crash the sync.
- Duplicate rows are not imported repeatedly.
- Sync result reports imported, skipped, and failed rows.
- Secrets are not committed.

Dependencies:

- DATA-001.
- BE-006.

### BE-008: Implement Spending Analyzer

Description:

Calculate financial summary data from stored transactions.

Scope:

- Daily spending total.
- Weekly spending total.
- Monthly spending total.
- Top category for current period.
- Budget usage percentage.
- Simple risk level.

Acceptance Criteria:

- Analyzer returns daily, weekly, and monthly totals.
- Analyzer returns top category.
- Analyzer calculates budget usage.
- Analyzer assigns risk level: `low`, `medium`, or `high`.
- Unit tests cover normal, empty, and over-budget cases.

Dependencies:

- BE-006.

### BE-009: Connect Analyzer To Device State

Description:

Replace static mock state with rule-based state generated from analyzer output.

Scope:

- Convert analyzer result into `DeviceState`.
- Pick mood, LED, buzzer, and LCD lines.
- Keep messages within LCD constraints.
- Preserve mock/fallback behavior for empty data.

Acceptance Criteria:

- `/api/device/state` reflects stored transaction data.
- Over-budget state returns `panic` mood and red LED.
- Warning state returns `warning` mood and yellow LED.
- Healthy state returns `happy` mood and green LED.
- All LCD lines are max 16 characters.
- Tests cover at least healthy, warning, panic, and empty states.

Dependencies:

- BE-004.
- BE-008.

## Milestone 3: Personality

Goal: add richer device behavior while keeping deterministic fallbacks.

### BE-010: Add Rule-Based Message Engine

Description:

Create a message engine that turns analyzer output into short personality messages without AI.

Scope:

- Add reusable message generation function.
- Support multiple templates per risk level.
- Enforce LCD constraints.
- Return mood and priority metadata.

Acceptance Criteria:

- Message engine returns exactly two lines.
- Each line is max 16 characters.
- Messages vary across categories or risk levels.
- Tests verify length constraints.
- Device state endpoint uses this engine.

Dependencies:

- BE-009.

### BE-011: Add AI Message Generator

Description:

Use an AI API to generate short personality messages when enabled.

Scope:

- Add environment flag to enable AI.
- Add prompt builder.
- Call AI provider.
- Validate output against LCD constraints.
- Fall back to rule-based message on error.

Acceptance Criteria:

- AI generation is disabled by default unless configured.
- Prompt includes exact LCD constraints.
- AI output is validated before use.
- Invalid or failed AI output falls back to rule-based messages.
- No sensitive raw transaction notes are sent unless explicitly allowed.

Dependencies:

- BE-010.

### FW-007: Add Buzzer Patterns

Description:

Play buzzer sounds based on `buzzer` field from device state.

Scope:

- `silent`: no sound.
- `soft`: short beep.
- `alert`: multiple beeps.
- Avoid repeated annoying beeps on every loop unless state changes or enough time has passed.

Acceptance Criteria:

- Buzzer pin is configured.
- `silent` produces no sound.
- `soft` produces one short beep.
- `alert` produces multiple beeps.
- Buzzer behavior is documented.

Dependencies:

- FW-006.

### FW-008: Add Button Mute

Description:

Use the physical button to mute current alert sounds.

Scope:

- Configure button GPIO.
- Debounce button input.
- Toggle or activate mute.
- Keep visual LCD and LED feedback active.

Acceptance Criteria:

- Button press is detected reliably.
- Muted state suppresses buzzer.
- Muted state does not stop LCD or LED updates.
- Serial logs show mute state changes.
- Debounce prevents repeated accidental toggles.

Dependencies:

- FW-007.

## Milestone 4: Stable Daily Companion

Goal: make the system reliable enough for daily use.

### OPS-001: Add Environment Configuration

Description:

Standardize backend configuration using environment variables and examples.

Scope:

- Add `.env.example`.
- Document required and optional environment variables.
- Ensure backend reads config from environment.
- Ignore local `.env`.

Acceptance Criteria:

- `.env.example` exists.
- Local `.env` is ignored.
- Backend starts with sensible local defaults.
- Missing required production settings produce a clear error.

Dependencies:

- BE-001.

### OPS-002: Add Docker Support

Description:

Make backend runnable through Docker for stable local deployment.

Scope:

- Add backend Dockerfile.
- Add docker compose file if useful.
- Mount or persist SQLite database.
- Document Docker commands.

Acceptance Criteria:

- Backend can run in Docker.
- `/api/health` works from Docker container.
- SQLite data can persist across container restarts.
- Docker docs are included.

Dependencies:

- BE-006.
- OPS-001.

### OPS-003: Add Basic Logging

Description:

Add useful backend logs for sync, analysis, API requests, and errors.

Scope:

- Log application startup.
- Log sheet sync summary.
- Log device state generation.
- Log AI fallback events.
- Avoid logging secrets.

Acceptance Criteria:

- Logs are readable in local terminal.
- Sync result logs imported/skipped/failed row counts.
- Device state generation logs mood and risk level.
- No secret values appear in logs.

Dependencies:

- BE-009.

### SEC-001: Add Device API Key Authentication

Description:

Protect device endpoints before using real financial data.

Scope:

- Require `X-Device-Key` header for `/api/device/state`.
- Keep `/api/health` public.
- Configure device key through environment variable.
- Document firmware config update.

Acceptance Criteria:

- `/api/device/state` rejects missing or invalid key.
- Valid key returns device state.
- `/api/health` remains public.
- Tests cover authorized and unauthorized requests.
- Firmware docs explain how to set the key.

Dependencies:

- OPS-001.
- BE-003.

### QA-001: Run 24 Hour Stability Test

Description:

Verify that the full device loop can run long enough to be useful.

Scope:

- Run backend continuously.
- Run ESP32 continuously.
- Observe reconnect behavior.
- Capture failures and fixes.

Acceptance Criteria:

- ESP32 runs for 24 hours.
- Device recovers from temporary backend outage.
- Device recovers from temporary WiFi outage.
- No repeated crash loop is observed.
- Test notes are added to docs.

Dependencies:

- FW-006.
- BE-009.

## Suggested Agent Execution Order

1. BE-001
2. BE-002
3. BE-003
4. BE-004
5. FW-001
6. FW-002
7. FW-003
8. FW-004
9. FW-005
10. FW-006
11. DATA-001
12. BE-005
13. BE-006
14. BE-007
15. BE-008
16. BE-009
17. BE-010
18. BE-011
19. FW-007
20. FW-008
21. OPS-001
22. OPS-002
23. OPS-003
24. SEC-001
25. QA-001
