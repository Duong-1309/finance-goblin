#pragma once

#include <Arduino.h>

#define PIN_RGB_R 18
#define PIN_RGB_G 19
#define PIN_RGB_B 23

// Common cathode: HIGH = on, LOW = off
// Set RGB_COMMON_CATHODE false in config.h for common anode
#ifndef RGB_COMMON_CATHODE
#define RGB_COMMON_CATHODE true
#endif

static void _set_rgb(bool r, bool g, bool b) {
#if RGB_COMMON_CATHODE
    digitalWrite(PIN_RGB_R, r ? HIGH : LOW);
    digitalWrite(PIN_RGB_G, g ? HIGH : LOW);
    digitalWrite(PIN_RGB_B, b ? HIGH : LOW);
#else
    digitalWrite(PIN_RGB_R, r ? LOW : HIGH);
    digitalWrite(PIN_RGB_G, g ? LOW : HIGH);
    digitalWrite(PIN_RGB_B, b ? LOW : HIGH);
#endif
}

void led_init() {
    pinMode(PIN_RGB_R, OUTPUT);
    pinMode(PIN_RGB_G, OUTPUT);
    pinMode(PIN_RGB_B, OUTPUT);
    _set_rgb(false, false, false);
    Serial.println("[led] init");
}

// led value: green / yellow / red / blue / white
void led_set(const char* color) {
    Serial.print("[led] color: ");
    Serial.println(color);

    if      (strcmp(color, "green")  == 0) _set_rgb(false, true,  false);
    else if (strcmp(color, "yellow") == 0) _set_rgb(true,  true,  false);
    else if (strcmp(color, "red")    == 0) _set_rgb(true,  false, false);
    else if (strcmp(color, "blue")   == 0) _set_rgb(false, false, true);
    else                                   _set_rgb(true,  true,  true);  // white / unknown
}
