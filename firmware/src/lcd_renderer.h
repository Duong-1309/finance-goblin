#pragma once

#include <Arduino.h>

// Stub: logs to Serial. Replace with real LCD driver when hardware is ready.
void lcd_init() {
    Serial.println("[lcd] init (serial stub)");
}

void lcd_render(const char* line1, const char* line2) {
    Serial.println("[lcd] ┌────────────────┐");
    Serial.print(  "[lcd] │");
    Serial.print(line1);
    for (int i = strlen(line1); i < 16; i++) Serial.print(' ');
    Serial.println("│");
    Serial.print(  "[lcd] │");
    Serial.print(line2);
    for (int i = strlen(line2); i < 16; i++) Serial.print(' ');
    Serial.println("│");
    Serial.println("[lcd] └────────────────┘");
}

void lcd_offline() {
    lcd_render("Backend offline", "Retrying...");
}
