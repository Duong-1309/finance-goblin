#pragma once

#include <Arduino.h>

#define PIN_BUTTON      4
#define DEBOUNCE_MS     50

static bool _muted           = false;
static bool _last_state      = HIGH;
static unsigned long _last_change_ms = 0;

void button_init() {
    pinMode(PIN_BUTTON, INPUT_PULLUP);
    Serial.println("[button] init");
}

// Call in loop() — returns true if button was just pressed (debounced)
bool button_was_pressed() {
    bool current = digitalRead(PIN_BUTTON);
    unsigned long now = millis();

    if (current != _last_state && (now - _last_change_ms) > DEBOUNCE_MS) {
        _last_state     = current;
        _last_change_ms = now;
        if (current == LOW) {  // active LOW (INPUT_PULLUP)
            return true;
        }
    }
    return false;
}

bool button_is_muted() { return _muted; }

void button_toggle_mute() {
    _muted = !_muted;
    Serial.print("[button] mute: ");
    Serial.println(_muted ? "ON" : "OFF");
}
