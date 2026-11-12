#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define BUZZER_PIN   18
#define GREEN_LED    19
#define TRIGGER_PIN  4   // D4 Magic Trigger Wire

LiquidCrystal_I2C lcd(0x27, 16, 2);
int last_state = -1; // Screen lag hatane ke liye state tracker

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(TRIGGER_PIN, INPUT_PULLUP);

  // Auto-detect LCD Address (0x27 or 0x3F)
  Wire.beginTransmission(0x27);
  if (Wire.endTransmission() != 0) {
    lcd = LiquidCrystal_I2C(0x3F, 16, 2);
  }

  lcd.init();
  lcd.backlight();
  lcd.clear();

  // Starting me hi Green LED ON aur Buzzer OFF
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(BUZZER_PIN, LOW);
}

void loop() {
  // Trigger check: Agar D4 GND se judi hai toh Fault (1), warna Healthy (0)
  int current_state = (digitalRead(TRIGGER_PIN) == LOW) ? 1 : 0;

  if (current_state == 0) {
    // ================= 1. HEALTHY STATE (Taar Bahar Hai) =================
    digitalWrite(GREEN_LED, LOW);  // Green LED PEHLE SE HI JALEGI (ON)
    digitalWrite(BUZZER_PIN, LOW); // Buzzer BILKUL CHUP (OFF)

    // Screen text (Sirf tab update hoga jab state badlegi)
    if (last_state != 0) {
      lcd.setCursor(0, 0);
      lcd.print("Vib:0.22g T:34C ");
      lcd.setCursor(0, 1);
      lcd.print("STATUS: HEALTHY ");
      last_state = 0;
    }

    // Dashboard Telemetry (Exact 85% Health Score)
    Serial.println("{\"rms\":0.220,\"temp\":34.0}");

  } else {
    // ================= 2. CRITICAL FAULT (Taar GND me Lagayi) =================
    digitalWrite(GREEN_LED, HIGH); // Green LED TURANT BAND (OFF)
    
    // Buzzer Siren Beep
    digitalWrite(BUZZER_PIN, (millis() / 120) % 2);

    if (last_state != 1) {
      lcd.setCursor(0, 0);
      lcd.print("Vib:1.10g T:60C ");
      lcd.setCursor(0, 1);
      lcd.print("CRITICAL DANGER!");
      last_state = 1;
    }

    // Dashboard Telemetry (Exact 15% Critical Score)
    Serial.println("{\"rms\":1.100,\"temp\":59.6}");
  }

  delay(50); // Instant 0-second response
}
