import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import plotly.graph_objects as go
import time
import json
import serial
import serial.tools.list_ports

st.set_page_config(page_title="AI CNC Predictive Maintenance", layout="wide", page_icon="⚙️")

# --- 1. TRAIN MACHINE LEARNING MODEL ---
@st.cache_resource
def train_ai_model():
    np.random.seed(42)
    n = 1500

    # Class 0: Healthy State (Normal vibration, normal temperature)
    c0_vib = np.random.normal(0.22, 0.05, n)
    c0_temp = np.random.normal(34, 3, n)
    c0_y = np.zeros(n)

    # Class 1: Critical Breakdown / Tool Failure
    c1_vib = np.random.normal(1.10, 0.15, n)
    c1_temp = np.random.normal(60, 5, n)
    c1_y = np.ones(n)

    X_vib = np.concatenate([c0_vib, c1_vib])
    X_temp = np.concatenate([c0_temp, c1_temp])
    y = np.concatenate([c0_y, c1_y])

    df = pd.DataFrame({'rms_vib': X_vib, 'temperature': X_temp})
    model = RandomForestClassifier(n_estimators=30, random_state=42)
    model.fit(df, y)
    return model

ai_model = train_ai_model()

# --- 2. HEADER UI ---
st.title("⚙️ AI-Driven Predictive Maintenance System for CNC Machines")
st.markdown("**Industry 4.0 Telemetry & Real-Time Machine Learning Diagnostic Suite**")

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("🛠️ Data Source Settings")
mode = st.sidebar.radio("Select Mode:", ["Live ESP32 Hardware Mode", "Simulation / Demo Mode"])

ser = None
if mode == "Live ESP32 Hardware Mode":
    ports = [p.device for p in serial.tools.list_ports.comports()]
    if ports:
        selected_port = st.sidebar.selectbox("Select COM Port:", ports)
        try:
            ser = serial.Serial(selected_port, 115200, timeout=0.5)
            st.sidebar.success(f"Connected to {selected_port}")
        except Exception as e:
            st.sidebar.error(f"Error opening port: {e}")
    else:
        st.sidebar.warning("No COM Port found. Connect ESP32 via USB!")

# --- 4. DATA INGESTION ---
curr_vib = 0.220
curr_temp = 34.0

if mode == "Simulation / Demo Mode":
    st.sidebar.subheader("Demo Controls")
    sim_state = st.sidebar.selectbox("Simulate Condition:", ["Healthy Spindle (85%)", "Critical Failure (15%)"])
    if sim_state == "Healthy Spindle (85%)":
        curr_vib = 0.220
        curr_temp = 34.0
    else:
        curr_vib = 1.100
        curr_temp = 59.6
else:
    # Read from Serial COM Port
    if ser and ser.is_open:
        try:
            # Flush extra buffer to get the freshest packet
            while ser.in_waiting > 100:
                ser.readline()
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("{") and line.endswith("}"):
                data = json.loads(line)
                curr_vib = float(data.get("rms", 0.220))
                curr_temp = float(data.get("temp", 34.0))
        except:
            pass

# --- 5. AI PREDICTION ---
input_df = pd.DataFrame({'rms_vib': [curr_vib], 'temperature': [curr_temp]})
prediction = int(ai_model.predict(input_df)[0])
probs = ai_model.predict_proba(input_df)[0]

# Calculate Machine Health Index (0 - 100%)
# Healthy (0.22, 34) -> 85%
# Critical (1.10, 59.6) -> 15%
health_score = max(5, int(100 - (curr_vib * 45 + max(0, curr_temp - 30) * 1.2)))

# --- 6. DISPLAY METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("RMS Vibration", f"{curr_vib:.3f} g")
col2.metric("Spindle Temp", f"{curr_temp:.1f} °C")
col3.metric("Health Index", f"{health_score}%")

if prediction == 0 and health_score > 50:
    col4.success("STATUS: HEALTHY")
    st.info("💡 **AI Diagnosis:** Normal condition. Spindle vibration and thermal signatures within safe ISO 10816 limits.")
else:
    col4.error("STATUS: CRITICAL DANGER")
    st.error("💡 **AI Diagnosis:** High probability of Spindle/Tool failure! Automated shutdown recommended.")

# --- 7. CHARTS ---
gcol1, gcol2 = st.columns(2)

with gcol1:
    bar_color = "#2ecc71" if health_score > 50 else "#e74c3c"
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = health_score,
        title = {'text': "CNC Machine Health Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': bar_color},
            'steps': [
                {'range': [0, 40], 'color': "rgba(231, 76, 60, 0.2)"},
                {'range': [40, 70], 'color': "rgba(243, 156, 18, 0.2)"},
                {'range': [70, 100], 'color': "rgba(46, 204, 113, 0.2)"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 40}
        }
    ))
    fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with gcol2:
    healthy_pct = probs[0] * 100 if len(probs) > 1 else (100 if prediction == 0 else 0)
    critical_pct = probs[1] * 100 if len(probs) > 1 else (0 if prediction == 0 else 100)
    fig_prob = go.Figure(data=[
        go.Bar(
            x=['Healthy Operation', 'Catastrophic Failure Risk'],
            y=[healthy_pct, critical_pct],
            marker_color=['#2ecc71', '#e74c3c']
        )
    ])
    fig_prob.update_layout(
        title="AI Probability Distribution (%)",
        yaxis=dict(range=[0, 100]),
        height=280,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_prob, use_container_width=True)

# Auto-refresh loop for live hardware telemetry
if mode == "Live ESP32 Hardware Mode":
    time.sleep(0.3)
    st.rerun()
