#pragma once

#include <Arduino.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define HTTP_TIMEOUT_MS 5000

struct DeviceState {
    char line1[17];       // max 16 chars + null
    char line2[17];
    char mood[10];        // happy/warning/panic/sleep/offline
    char led[10];         // green/yellow/red/blue/white
    char buzzer[10];      // silent/soft/alert
    int  refresh_after;   // seconds
    bool valid;           // false = offline/parse error
};

DeviceState offline_state() {
    DeviceState s;
    strncpy(s.line1,        "Backend offline", 16); s.line1[16] = '\0';
    strncpy(s.line2,        "Retrying...",     16); s.line2[16] = '\0';
    strncpy(s.mood,         "offline",          9); s.mood[9]   = '\0';
    strncpy(s.led,          "white",            9); s.led[9]    = '\0';
    strncpy(s.buzzer,       "silent",           9); s.buzzer[9] = '\0';
    s.refresh_after = 60;
    s.valid = false;
    return s;
}

DeviceState fetch_device_state(const char* backend_url) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[api] no WiFi, skipping fetch");
        return offline_state();
    }

    String url = String(backend_url) + "/api/device/state";
    Serial.print("[api] GET ");
    Serial.println(url);

    HTTPClient http;
    http.begin(url);
    http.setTimeout(HTTP_TIMEOUT_MS);

    int status = http.GET();

    if (status != 200) {
        Serial.print("[api] error, HTTP status: ");
        Serial.println(status);
        http.end();
        return offline_state();
    }

    String body = http.getString();
    http.end();

    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, body);
    if (err) {
        Serial.print("[api] JSON parse error: ");
        Serial.println(err.c_str());
        return offline_state();
    }

    DeviceState s;
    strncpy(s.line1,   doc["line1"]        | "               ", 16); s.line1[16]  = '\0';
    strncpy(s.line2,   doc["line2"]        | "               ", 16); s.line2[16]  = '\0';
    strncpy(s.mood,    doc["mood"]         | "offline",          9); s.mood[9]    = '\0';
    strncpy(s.led,     doc["led"]          | "white",            9); s.led[9]     = '\0';
    strncpy(s.buzzer,  doc["buzzer"]       | "silent",           9); s.buzzer[9]  = '\0';
    s.refresh_after = doc["refresh_after"] | 60;
    s.valid = true;

    if (s.refresh_after <= 0) s.refresh_after = 60;

    Serial.print("[api] line1: ");        Serial.println(s.line1);
    Serial.print("[api] line2: ");        Serial.println(s.line2);
    Serial.print("[api] mood: ");         Serial.println(s.mood);
    Serial.print("[api] led: ");          Serial.println(s.led);
    Serial.print("[api] buzzer: ");       Serial.println(s.buzzer);
    Serial.print("[api] refresh_after: ");Serial.println(s.refresh_after);

    return s;
}
