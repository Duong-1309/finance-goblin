#include <Arduino.h>

#include "config.h"
#include "api_client.h"
#include "button_handler.h"
#include "buzzer_controller.h"
#include "lcd_renderer.h"
#include "led_controller.h"
#include "mqtt_client.h"
#include "wifi_manager.h"

#define DEFAULT_REFRESH_S 60

static DeviceState g_state;

static void apply_state(const DeviceState& state) {
    if (state.valid) {
        lcd_render(state.line1, state.line2);
        led_set(state.led);
    } else {
        lcd_offline();
        led_set("white");
    }
}

// Called by mqtt_client.h when goblin/display message arrives
void on_mqtt_display(const char* line1, const char* line2,
                     const char* mood, const char* led,
                     const char* buzzer, int refresh_after) {
    Serial.println("[main] MQTT push received — updating display");
    DeviceState s;
    strncpy(s.line1, line1, 16); s.line1[16] = '\0';
    strncpy(s.line2, line2, 16); s.line2[16] = '\0';
    strncpy(s.mood,  mood,   9); s.mood[9]   = '\0';
    strncpy(s.led,   led,    9); s.led[9]    = '\0';
    strncpy(s.buzzer, buzzer, 9); s.buzzer[9] = '\0';
    s.refresh_after = refresh_after > 0 ? refresh_after : DEFAULT_REFRESH_S;
    s.valid = true;
    g_state = s;
    apply_state(g_state);
    if (!button_is_muted()) {
        buzzer_play(g_state.buzzer, true, g_state.mood);  // force play on push event
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("[finance-goblin] booting...");

    lcd_init();
    led_init();
    buzzer_init();
    button_init();

    wifi_connect(WIFI_SSID, WIFI_PASSWORD);

    mqtt_setup();
    mqtt_connect();

    g_state = fetch_device_state(BACKEND_URL);
    apply_state(g_state);
    if (!button_is_muted()) {
        buzzer_play(g_state.buzzer, false, g_state.mood);
    }
}

void loop() {
    // Handle MQTT incoming messages
    mqtt_loop();

    // Handle button press → toggle mute
    if (button_was_pressed()) {
        button_toggle_mute();
        if (button_is_muted()) buzzer_mute();
    }

    // Reconnect WiFi if dropped
    if (!wifi_is_connected()) {
        Serial.println("[main] WiFi lost, reconnecting...");
        wifi_connect(WIFI_SSID, WIFI_PASSWORD);
    }

    // HTTP polling as fallback (keeps display fresh even if MQTT missed)
    g_state = fetch_device_state(BACKEND_URL);
    apply_state(g_state);
    if (!button_is_muted()) {
        buzzer_play(g_state.buzzer, false, g_state.mood);
    }

    int wait_s = (g_state.valid && g_state.refresh_after > 0)
                     ? g_state.refresh_after
                     : DEFAULT_REFRESH_S;

    Serial.print("[main] next poll in ");
    Serial.print(wait_s);
    Serial.println("s");

    // Poll button + MQTT during wait instead of blocking delay
    unsigned long deadline = millis() + (unsigned long)wait_s * 1000;
    while (millis() < deadline) {
        mqtt_loop();
        if (button_was_pressed()) {
            button_toggle_mute();
            if (button_is_muted()) buzzer_mute();
        }
        delay(20);
    }
}
