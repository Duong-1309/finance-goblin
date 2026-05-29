# API Specification

## Authentication

MVP can start without authentication on local network. Before using real financial data, add API key authentication.

Recommended header:

```txt
X-Device-Key: <secret>
```

## GET /api/health

Returns backend health.

### Response

```json
{
  "status": "ok"
}
```

## GET /api/device/state

Returns the current state the ESP32 should render.

### Response

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

## Device State Fields

| Field | Type | Notes |
| --- | --- | --- |
| line1 | string | LCD first line, max 16 chars |
| line2 | string | LCD second line, max 16 chars |
| mood | string | `happy`, `warning`, `panic`, `sleep`, `offline` |
| led | string | `green`, `yellow`, `red`, `blue`, `white` |
| buzzer | string | `silent`, `soft`, `alert` |
| refresh_after | number | seconds until next fetch |

## Error Behavior

If the backend fails, the ESP32 should show:

```txt
Backend offline
Retrying...
```

The LED should switch to white.
