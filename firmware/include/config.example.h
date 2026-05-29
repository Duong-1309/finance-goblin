#pragma once

// Copy this file to config.h and fill in your local values.
// config.h is gitignored — never commit it.

// WiFi credentials
#define WIFI_SSID     "your-wifi-ssid"
#define WIFI_PASSWORD "your-wifi-password"

// Backend URL (no trailing slash)
// Local development example: "http://192.168.1.100:8000"
#define BACKEND_URL   "http://your-backend-ip:8000"

// RGB LED wiring assumption: common cathode (LOW = off, HIGH = on).
// Change LED logic in led_controller if using common anode.
#define RGB_COMMON_CATHODE true
