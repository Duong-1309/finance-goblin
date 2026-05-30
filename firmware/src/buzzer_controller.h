#pragma once

#include <Arduino.h>

#include "config.h"

#define PIN_BUZZER 5

// Note frequencies — shifted up 2 octaves for cheap passive buzzers (resonance ~2-4kHz)
#define NOTE_C4  1047
#define NOTE_E4  1319
#define NOTE_G4  1568
#define NOTE_C5  2093
#define NOTE_E5  2637
#define NOTE_G5  3136
#define NOTE_A5  3520

// Cooldown: don't repeat same pattern within 5 minutes
static String        _last_buzzer   = "";
static unsigned long _last_buzz_ms  = 0;
#define BUZZ_COOLDOWN_MS 300000

// ── Internal helpers ──────────────────────────────────────────

static void _beep_active(int duration_ms) {
    digitalWrite(PIN_BUZZER, HIGH);
    delay(duration_ms);
    digitalWrite(PIN_BUZZER, LOW);
}

static void _note(int freq, int duration_ms) {
    tone(PIN_BUZZER, freq, duration_ms);
    delay(duration_ms + 20);  // small gap between notes
    noTone(PIN_BUZZER);
}

// ── Melodies (passive buzzer) ─────────────────────────────────

static void _melody_soft() {
    _note(NOTE_C5, 150);
}

static void _melody_happy() {
    _note(NOTE_C5, 100);
    _note(NOTE_E5, 100);
    _note(NOTE_G5, 200);
}

static void _melody_warning() {
    _note(NOTE_G4, 100);
    _note(NOTE_E4, 150);
    delay(80);
    _note(NOTE_G4, 100);
    _note(NOTE_E4, 150);
}

static void _melody_panic() {
    for (int i = 0; i < 4; i++) {
        _note(NOTE_A5, 80);
        _note(NOTE_C4, 80);
    }
}

static void _melody_offline() {
    _note(NOTE_G4, 150);
    _note(NOTE_E4, 150);
    _note(NOTE_C4, 250);
}

// ── Beep patterns (active buzzer) ────────────────────────────

static void _beep_soft() {
    _beep_active(100);
}

static void _beep_alert() {
    _beep_active(200); delay(100);
    _beep_active(200); delay(100);
    _beep_active(200);
}

// ── Public API ────────────────────────────────────────────────

void buzzer_init() {
    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);
    Serial.println("[buzzer] init");
}

// pattern: "silent" | "soft" | "alert"
// mood:    "happy" | "warning" | "panic" | "sleep" | "offline" (used for melody selection)
void buzzer_play(const char* pattern, bool force = false, const char* mood = "") {
    unsigned long now = millis();
    bool same   = (_last_buzzer == String(pattern));
    bool cooled = (now - _last_buzz_ms > BUZZ_COOLDOWN_MS);

    if (same && !cooled && !force) return;

    _last_buzzer  = String(pattern);
    _last_buzz_ms = now;

    if (strcmp(pattern, "silent") == 0) {
        // no sound
    } else if (strcmp(pattern, "soft") == 0) {
#if BUZZER_PASSIVE
        // pick melody by mood if provided, else default soft note
        if (strcmp(mood, "happy") == 0)        _melody_happy();
        else if (strcmp(mood, "offline") == 0) _melody_offline();
        else                                   _melody_soft();
#else
        _beep_soft();
#endif
    } else if (strcmp(pattern, "alert") == 0) {
#if BUZZER_PASSIVE
        if (strcmp(mood, "warning") == 0) _melody_warning();
        else                              _melody_panic();
#else
        _beep_alert();
#endif
    }

    Serial.print("[buzzer] ");
    Serial.print(pattern);
    if (strlen(mood) > 0) { Serial.print(" ("); Serial.print(mood); Serial.print(")"); }
    Serial.println();
}

void buzzer_mute() {
    _last_buzzer  = "silent";
    _last_buzz_ms = millis();
    noTone(PIN_BUZZER);
    digitalWrite(PIN_BUZZER, LOW);
    Serial.println("[buzzer] muted");
}
