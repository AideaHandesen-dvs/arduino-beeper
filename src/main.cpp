#include <Arduino.h>

const int BUZZER_PIN = 9;
char buf[32];
int idx = 0;

void processCommand(const char* cmd) {
    int freq = 0;
    int duration = 0;
    
    const char* f = strchr(cmd, 'F');
    const char* d = strchr(cmd, 'D');
    
    if (f) freq = atoi(f + 1);
    if (d) duration = atoi(d + 1);
    
    if (freq > 0 && duration > 0) {
        tone(BUZZER_PIN, freq, duration);
        Serial.print("OK ");
        Serial.print(freq);
        Serial.print("Hz ");
        Serial.print(duration);
        Serial.println("ms");
    } else {
        Serial.println("ERR");
    }
}

void setup() {
    pinMode(6, OUTPUT);
    digitalWrite(6, LOW);

    Serial.begin(9600);
    pinMode(BUZZER_PIN, OUTPUT);
    Serial.println("BEEPER READY");

    // PC-98風起動音
    tone(BUZZER_PIN, 2000, 100);
    delay(120);
    tone(BUZZER_PIN, 4000, 100);
}

void loop() {
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
            buf[idx] = '\0';
            if (idx > 0) {
                processCommand(buf);
            }
            idx = 0;
        } else if (idx < 31) {
            buf[idx++] = c;
        }
    }
}
