# Finance Goblin — Firmware

ESP32 firmware for the Finance Goblin desk companion. Uses Arduino framework via PlatformIO.

## Hardware (MVP)

| Component | GPIO |
|-----------|------|
| LCD SDA   | 21   |
| LCD SCL   | 22   |
| RGB Red   | 18   |
| RGB Green | 19   |
| RGB Blue  | 23   |
| Buzzer    | 5    |
| Button    | 4    |

RGB LED wiring assumes **common cathode**. See `include/config.example.h` to change.

## Setup

### 1. Install PlatformIO

```bash
pip install platformio
```

Or install the [PlatformIO IDE extension](https://platformio.org/install/ide) for VS Code.

### 2. Create local config

```bash
cp include/config.example.h include/config.h
```

Edit `include/config.h` and fill in:

- `WIFI_SSID` — your WiFi network name
- `WIFI_PASSWORD` — your WiFi password
- `BACKEND_URL` — backend IP and port, e.g. `http://192.168.1.100:8000`

`config.h` is gitignored and must never be committed.

## Build

```bash
cd firmware
pio run
```

## Flash

```bash
pio run --target upload
```

## Serial Monitor

```bash
pio device monitor
```

Baud rate: 115200

## Color Mapping

| LED color | Mood    |
|-----------|---------|
| Green     | happy   |
| Yellow    | warning |
| Red       | panic   |
| Blue      | sleep   |
| White     | offline |
