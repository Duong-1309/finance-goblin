# Hardware Wiring

## Current Components

- ESP32
- LCD1602
- RGB LED
- buzzer
- button
- RFID module
- servo motor
- sensors

## MVP Components

Only these are required for the first build:

- ESP32
- LCD1602 with I2C module
- RGB LED
- buzzer
- button

## Wiring Plan

| Component | GPIO |
| --- | --- |
| LCD SDA | GPIO21 |
| LCD SCL | GPIO22 |
| RGB Red | GPIO18 |
| RGB Green | GPIO19 |
| RGB Blue | GPIO23 |
| Buzzer | GPIO5 |
| Button | GPIO4 |

## Recommended Additional Hardware

Later:

- OLED SSD1306
- LED ring
- ESP32-CAM
- speaker module
- motion sensor
- ultrasonic sensor

## Notes

- Use resistors for RGB LED pins.
- Confirm whether the RGB LED is common anode or common cathode before writing LED logic.
- Use I2C scanner firmware if the LCD address is unknown.
