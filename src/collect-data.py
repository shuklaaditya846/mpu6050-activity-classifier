import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime

default_baud_rate = 115200

def list_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def read_serial(port, baudrate=default_baud_rate, save=False, filename="serial_data.txt", recording_duration=-1):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"\nReading from {port} at {baudrate} baud. Press Ctrl+C to stop.\n")
        start_time = time.time()
        
        with open(filename, "w") if save else open(filename, "w") as f:
            try:
                while True:
                    if recording_duration and (time.time() - start_time) >= recording_duration:
                        print(f"\nRecording stopped after {recording_duration} seconds.")
                        break
                    line = ser.readline().decode(errors='ignore').strip()
                    if line:
                        print(line)
                        if save:
                            f.write(line + "\n")
            except KeyboardInterrupt:
                print(f"\nStopped reading. File '{filename}' saved.")
            finally:
                ser.close()

    except serial.SerialException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ports = list_ports()
    if not ports:
        print("No COM ports found.")
        exit()

    print("Available COM ports:")
    for i, p in enumerate(ports):
        print(f"{i+1}. {p}")

    choice = int(input("Select port number: ")) - 1
    if choice < 0 or choice >= len(ports):
        print("Invalid choice.")
        exit()

    baudrate = input(f"Enter baudrate (default {default_baud_rate}): ") or default_baud_rate
    save = input("Save data to file? (leave empty for 'y') (y/n): ").lower() == "y" or "y"    # save by default

    current_time = str(datetime.now())
    current_time = current_time.replace(" ", "_")
    current_time = current_time.replace(".", "-")
    current_time = current_time.replace(":", "-")
    filename = f"serial_data_{current_time}.txt"
    if save:
        filename = input(f"Enter filename (default {filename}): ") or filename

    recording_duration = input(f"Enter recording session length (in seconds, viz. 3 for 3 seconds) (default is infinitely long): ").strip()
    recording_duration = float(recording_duration) if recording_duration else None

    read_serial(ports[choice], int(baudrate), save, filename, recording_duration)
