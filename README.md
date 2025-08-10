# MPU6050 Activity Classifier

## 📌 Overview
This project collects accelerometer and gyroscope data from an **MPU6050 sensor**, processes it, and classifies activities (e.g., walking, running, idle) using a machine learning model.  
It demonstrates **sensor data processing, feature engineering, and real-time inference**.

---

## ⚙️ Features
- **Arduino + MPU6050** for data acquisition
- Serial communication to Python for logging
- Data preprocessing & feature extraction (statistical + frequency domain)
- Model training (RandomForest / TensorFlow)
- Real-time predictions
- Demo video + code for reproducibility

---

## 🛠️ Tech Stack
- **Hardware:** ESP8266 Microcontroller + MPU6050
- **C++:** Code for the microcontroller
- **Python:** pandas, numpy, scikit-learn, FastAPI
- **ML:** RandomForest, TensorFlow
- **Other:** matplotlib, seaborn (EDA), plotly

---

## 📂 Repo Structure
See `repo_structure` section above.

---

## 🚀 Getting Started
### 1️⃣ Hardware Setup
- Connect MPU6050 → Arduino as per `hardware/wiring_diagram.png`
- Upload `hardware/arduino_mpu6050.ino` to Arduino.

### 2️⃣ Data Collection
```bash
python src/data_collection.py
