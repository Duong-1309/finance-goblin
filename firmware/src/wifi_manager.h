#pragma once

#include <Arduino.h>
#include <WiFi.h>

// Attempts WiFi connection, retrying up to max_attempts times.
// Prints status to Serial. Returns true if connected.
bool wifi_connect(const char* ssid, const char* password, int max_attempts = 20) {
    Serial.print("[wifi] connecting to ");
    Serial.println(ssid);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < max_attempts) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.print("[wifi] connected, IP: ");
        Serial.println(WiFi.localIP());
        return true;
    }

    Serial.println("[wifi] connection failed");
    return false;
}

bool wifi_is_connected() {
    return WiFi.status() == WL_CONNECTED;
}
