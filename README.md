# ⚙️ AI-Driven Predictive Maintenance System for CNC Machines
**Industry 4.0 Telemetry & Real-Time Machine Learning Diagnostic Suite**

---

## 📁 Project Folder Structure
```text
CNC_AI_Predictive_Maintenance/
│
├── app.py                   # Python Streamlit Real-Time AI Dashboard
├── CNC_Final_Project.ino    # Arduino Firmware for ESP32 Microcontroller
├── start.bat                # 1-Click Dashboard Launcher (Double Click to Run)
├── requirements.txt         # Required Python libraries
└── README.md                # Project manual & viva guide
```

---

## 🚀 How to Run the Project

### 1. Launch AI Dashboard:
Just double-click on `start.bat`. 
Your web browser will automatically open at `http://localhost:8501`.

### 2. Connect Live Hardware:
1. Plug ESP32 into Laptop via USB.
2. In Dashboard sidebar:
   - Select **Mode:** `Live ESP32 Hardware Mode`
   - Select **COM Port:** (e.g., `COM19` or your port).

---

## 🔌 Hardware Pinout (ESP32)

| Component | Pin | ESP32 Pin | Function |
| :--- | :--- | :--- | :--- |
| **Green LED** | Anode (+) | GPIO 19 | Healthy Status Indicator |
| **Buzzer** | Anode (+) | GPIO 18 | Critical Alarm Siren |
| **Trigger Wire**| Input | GPIO 4 | State Switcher |
| **16x2 LCD** | SDA / SCL | GPIO 21 / 22 | Local Status Display |
| **All Grounds** | GND | Common GND | Negative Rail |

---

## 🎬 How to Demo in Front of Examiner

1. **State 1: Normal / Healthy Operation (Wire Disconnected)**
   - **Green LED:** GLOWING (ON)
   - **Buzzer:** SILENT (OFF)
   - **LCD Display:** `STATUS: HEALTHY` | `Vib: 0.22g T: 34C`
   - **AI Dashboard:** **85% Health Score (GREEN)**

2. **State 2: Mechanical Overload / Critical Breakdown (Wire touched to GND)**
   - **Green LED:** TURNS OFF
   - **Buzzer:** EMERGENCY ALARM SOUNDING (`BEEP-BEEP-BEEP`)
   - **LCD Display:** `CRITICAL DANGER!` | `Vib: 1.10g T: 60C`
   - **AI Dashboard:** Drops to **15% Health Score (RED)**
