# Firmware Design

## Modules

```txt
wifi_manager
api_client
lcd_renderer
led_controller
buzzer_controller
button_handler
state_machine
```

## wifi_manager

Responsibilities:

- connect to WiFi
- handle reconnects
- expose network status

## api_client

Responsibilities:

- fetch backend state
- parse JSON response
- retry failed requests
- handle API timeout

## lcd_renderer

Responsibilities:

- render two lines of text
- truncate long text
- clear and redraw display
- show offline/error message

## led_controller

Responsibilities:

- map mood to color
- apply blink effects
- support simple transitions

## buzzer_controller

Responsibilities:

- play sound patterns
- respect alert priority
- support mute behavior

## button_handler

Responsibilities:

- mute current alert
- show next message later
- expose debug action later

## state_machine

Device states:

| State | Description |
| --- | --- |
| BOOTING | Device startup |
| WIFI_CONNECTING | Connecting to WiFi |
| FETCHING | Calling backend |
| DISPLAYING | Rendering state |
| ALERTING | Buzzer or LED alert |
| IDLE | Waiting for refresh |
| ERROR | Error mode |
| OFFLINE | Backend unreachable |

## First Firmware Target

The first firmware version only needs:

- WiFi connection
- HTTP GET to `/api/device/state`
- JSON parsing
- LCD render
- RGB LED color mapping
