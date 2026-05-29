#include <Arduino.h>
#include "config.h"
#include "wifi_manager.h"
#include "api_client.h"
#include "lcd_renderer.h"
#include "led_controller.h"
#include "buzzer_controller.h"
#include "button_handler.h"

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

void setup() {
    Serial.begin(115200);
    Serial.println("[finance-goblin] booting...");

    lcd_init();
    led_init();
    buzzer_init();
    button_init();

    wifi_connect(WIFI_SSID, WIFI_PASSWORD);

    g_state = fetch_device_state(BACKEND_URL);
    apply_state(g_state);

    if (!button_is_muted()) {
        buzzer_play(g_state.buzzer);
    }
}

void loop() {
    // Handle button press → toggle mute
    if (button_was_pressed()) {
        button_toggle_mute();
        if (button_is_muted()) {
            buzzer_mute();
        }
    }

    // Reconnect WiFi if dropped
    if (!wifi_is_connected()) {
        Serial.println("[main] WiFi lost, reconnecting...");
        wifi_connect(WIFI_SSID, WIFI_PASSWORD);
    }

    g_state = fetch_device_state(BACKEND_URL);
    apply_state(g_state);

    if (!button_is_muted()) {
        buzzer_play(g_state.buzzer);
    }

    int wait_s = (g_state.valid && g_state.refresh_after > 0)
                 ? g_state.refresh_after
                 : DEFAULT_REFRESH_S;

    Serial.print("[main] next fetch in ");
    Serial.print(wait_s);
    Serial.println("s");

    // Poll button during wait instead of blocking with delay()
    unsigned long deadline = millis() + (unsigned long)wait_s * 1000;
    while (millis() < deadline) {
        if (button_was_pressed()) {
            button_toggle_mute();
            if (button_is_muted()) buzzer_mute();
        }
        delay(20);
    }
}
