import serial
import threading
import joblib
import numpy as np
# from tensorflow.keras.models import load_model
from collections import deque

# Load models
rf_model = joblib.load("random_forest_model.pkl")
# lstm_model = load_model("lstm_model.keras")

# Serial port config
ser = serial.Serial('COM3', baudrate=115200, timeout=1)

# Buffer for LSTM (sliding window)
window_size = 50  # depends on your training
lstm_buffer = deque(maxlen=window_size)

actions = ["idle_noise", "rear_hook", "rear_uppercut", "wave"]
last_action = None

def process_data():
    global last_action
    while True:
        line = ser.readline().decode().strip()
        if not line:
            continue
        
        try:
            values = list(map(float, line.split(',')))  # sensor data
        except:
            continue
        
        # Random Forest expects flat features
        rf_pred = rf_model.predict([values])[0]
        
        # LSTM expects sequence
        lstm_buffer.append(values)
        if len(lstm_buffer) == window_size:
            seq = np.array(lstm_buffer).reshape(1, window_size, len(values))
            # lstm_pred = np.argmax(lstm_model.predict(seq, verbose=0))
            
            # Use one model or combine both
            # final_pred = actions[lstm_pred]  # or rf_pred
            final_pred = actions[rf_pred]
            
            if final_pred != last_action:
                print(f"Action: {final_pred}")
                last_action = final_pred

# Run in background
t = threading.Thread(target=process_data)
t.start()
