import streamlit as st
import serial
import time
import smtplib
from email.mime.text import MIMEText

def get_thresholds(age, gender):
    if gender == "Male":
        emg_thresh = 120 + (age * 0.3)
        temp_thresh = 37.5 + (age * 0.02)
    else:
        emg_thresh = 110 + (age * 0.25)
        temp_thresh = 37.2 + (age * 0.015)
    return emg_thresh, temp_thresh

def send_email_alert():
    msg = MIMEText("⚠️ Muscle fatigue detected. Please take rest.")
    msg['Subject'] = "Fatigue Alert"
    msg['From'] = "your_email@gmail.com"
    msg['To'] = "recipient@gmail.com"
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("your_email@gmail.com", "your_app_password")
    server.send_message(msg)
    server.quit()

st.title("💪 Muscle Fatigue Detection System")

age = st.slider("Enter Age", 10, 80, 25)
gender = st.selectbox("Select Gender", ["Male", "Female"])

emg_thresh, temp_thresh = get_thresholds(age, gender)

st.markdown(f"**EMG Threshold:** `{emg_thresh:.2f}`")
st.markdown(f"**Temp Threshold:** `{temp_thresh:.2f} °C`")

st.subheader("📡 Live Sensor Data")
emg_val_placeholder = st.empty()
temp_placeholder = st.empty()
status_placeholder = st.empty()

ser = serial.Serial("COM5", 115200)  # Update COM port as needed

while True:
    line = ser.readline().decode().strip()
    if ',' not in line:
        continue
    try:
        emg_val, temp_val = map(float, line.split(","))
    except:
        continue

    emg_val_placeholder.metric("EMG Envelope", f"{emg_val:.2f}")
    temp_placeholder.metric("Temperature (°C)", f"{temp_val:.2f}")

    if emg_val < emg_thresh and temp_val < temp_thresh:
        status = "Relaxed 😌"
    elif emg_val > emg_thresh and temp_val < temp_thresh:
        status = "Working 💪"
    elif emg_val > emg_thresh and temp_val > temp_thresh:
        status = "Fatigued 🚨"
        send_email_alert()
    else:
        status = "Unknown ❓"

    status_placeholder.markdown(f"### Status: **{status}**")
    time.sleep(0.5)
