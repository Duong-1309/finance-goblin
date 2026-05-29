#pragma once

#include <Arduino.h>

#define PIN_BUZZER 5

// Tracks last buzzer value and time to avoid repeating on every loop
static String  _last_buzzer   = "";
static unsigned long _last_buzz_ms = 0;
#define BUZZ_COOLDOWN_MS 300000  // 5 minutes between repeat alerts

void buzzer_init() {
    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);
    Serial.println("[buzzer] init");
}

static void _beep(int duration_ms) {
    digitalWrite(PIN_BUZZER, HIGH);
    delay(duration_ms);
    digitalWrite(PIN_BUZZER, LOW);
}

// buzzer value: silent / soft / alert
void buzzer_play(const char* pattern, bool force = false) {
    unsigned long now = millis();
    bool same = (_last_buzzer == String(pattern));
    bool cooled = (now - _last_buzz_ms > BUZZ_COOLDOWN_MS);

    if (same && !cooled && !force) {
        return;  // skip repeat within cooldown window
    }

    _last_buzzer  = String(pattern);
    _last_buzz_ms = now;

    if (strcmp(pattern, "silent") == 0) {
        // no sound
    } else if (strcmp(pattern, "soft") == 0) {
        _beep(100);
    } else if (strcmp(pattern, "alert") == 0) {
        _beep(200); delay(100);
        _beep(200); delay(100);
        _beep(200);
    }

    Serial.print("[buzzer] ");
    Serial.println(pattern);
}

void buzzer_mute() {
    _last_buzzer  = "silent";
    _last_buzz_ms = millis();
    digitalWrite(PIN_BUZZER, LOW);
    Serial.println("[buzzer] muted");
}
