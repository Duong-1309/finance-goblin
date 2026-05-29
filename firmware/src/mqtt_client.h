#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFi.h>

#include "config.h"

// Callback signature — main.cpp provides implementation
extern void on_mqtt_display(const char* line1, const char* line2,
                            const char* mood, const char* led,
                            const char* buzzer, int refresh_after);

static WiFiClient   _wifi_client;
static PubSubClient _mqtt(_wifi_client);

static void _mqtt_callback(char* topic, byte* payload, unsigned int length) {
    char buf[256];
    unsigned int len = length < sizeof(buf) - 1 ? length : sizeof(buf) - 1;
    memcpy(buf, payload, len);
    buf[len] = '\0';

    Serial.print("[mqtt] received on ");
    Serial.print(topic);
    Serial.print(": ");
    Serial.println(buf);

    JsonDocument doc;
    if (deserializeJson(doc, buf) != DeserializationError::Ok) {
        Serial.println("[mqtt] JSON parse error");
        return;
    }

    on_mqtt_display(
        doc["line1"]        | "               ",
        doc["line2"]        | "               ",
        doc["mood"]         | "offline",
        doc["led"]          | "white",
        doc["buzzer"]       | "silent",
        doc["refresh_after"] | 60
    );
}

void mqtt_setup() {
    _mqtt.setServer(MQTT_BROKER_IP, MQTT_PORT);
    _mqtt.setCallback(_mqtt_callback);
    Serial.println("[mqtt] configured");
}

bool mqtt_connect() {
    if (_mqtt.connected()) return true;

    Serial.print("[mqtt] connecting to ");
    Serial.print(MQTT_BROKER_IP);
    Serial.print("...");

    if (_mqtt.connect(MQTT_CLIENT_ID)) {
        _mqtt.subscribe(MQTT_TOPIC);
        Serial.println(" connected");
        Serial.print("[mqtt] subscribed to ");
        Serial.println(MQTT_TOPIC);
        return true;
    }

    Serial.print(" failed, rc=");
    Serial.println(_mqtt.state());
    return false;
}

// Call in loop() — handles reconnect (with 5s cooldown) + incoming messages
void mqtt_loop() {
    if (!_mqtt.connected()) {
        static unsigned long _last_attempt = 0;
        if (millis() - _last_attempt > 5000) {
            _last_attempt = millis();
            mqtt_connect();
        }
        return;
    }
    _mqtt.loop();
}
