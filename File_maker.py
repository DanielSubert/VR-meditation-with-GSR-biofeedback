import time
import pandas as pd
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
import os
import sys
import serial  # Import the serial library
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Configuration
DATA_ASSETS_DIR = "/Users/Daniel/Unity projects/RelaxAndMeditationVR-main 2/Assets"  # Directory to save data files
DATA_DIR = os.path.join(DATA_ASSETS_DIR, "GSRData")
READ_INTERVAL = 3  # How often to process data (seconds)
SERIAL_PORT = '/dev/cu.usbmodem1301'  # Update this to your Pico's serial port
BAUD_RATE = 9600
SERIAL_TIMEOUT = 4  # Timeout for serial read (slightly longer than READ_INTERVAL)
PREV_DATA = [] # check if being used?
BASELINE_COUNT = 10 # Number of values to use for baseline
GSR_BUFFER_SIZE = 5 # Number of recent GSR values to average
PERCENT_CHANCE_THRESHOLD = 0.05 # 5% change threshold for stress detection

baseline_values = [] # List to store baseline GSR values
baseline_average = 0.0 # Initiliase baseline average
baseline_collected = False # Flag to indicate if baseline has been collected
gsr_buffer = [] # Buffer to hold recent GSR values

# Function to read data from the serial port
def read_serial_data(serial_port, baud_rate, timeout):
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=timeout)
        # time.sleep(5)
        data = []
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if ser.in_waiting > 0:
               line = ser.readline().decode('utf-8').strip()
               match = re.search(r"(\d+\.\d{3}), (\d+\.\d+)", line)
               if match:
                  timestamp, gsr_value = match.groups()
                  data_point = ((float(timestamp), float(gsr_value)))
                  data.append(data_point)
        ser.close()
        return data
    except serial.SerialException as e:
        print(f"Serial errror: {e}")
        return []

# Function to calculate the baseline GSR value
def calculate_baseline(data, count):
   """Calculates the baseline GSR value from the first 'count' data points. (Count = 10)"""
   global baseline_average, baseline_collected
   if len(data) < count:
    return False # Not enough data to calculate baseline
   
   gsr_values = [float(pair[1]) for pair in data[:count]] # Extract GSR values
   baseline_average = sum(gsr_values) / count
   baseline_collected = True # Set the flag to indicate that baseline has been collected
   return True

# Function to do the data analysis using baseline -> TO BE REPLACED W/ ACTUAL ANALYSIS
def process_data(gsr_value):
  """Compares the given GSR value to the calculated baseline and returns 1 or 0.""" 
  global baseline_average, baseline_collected, gsr_buffer

  if not baseline_collected:
    return None # No baseline collected yet
  gsr_buffer.append(gsr_value)
  if len(gsr_buffer) > GSR_BUFFER_SIZE:
    gsr_buffer.pop(0) # Keep only the last 5 values

  if len(gsr_buffer) < GSR_BUFFER_SIZE:
    return None # Wait until we have enough values
  
  mean_value = sum(gsr_buffer) / len(gsr_buffer)
  normalized_change = (mean_value - baseline_average) / baseline_average

  if normalized_change < PERCENT_CHANCE_THRESHOLD:
    return 0
  else:
    return 1

# Function to check the files in the directory and make new file name w/ new number
def get_next_filename(data_dir):
    """Finds next available filename in the format data[number].txt"""
    files = [f for f in os.listdir(data_dir) if re.match(r"data(\d+)\.txt", f)]
    if not files:
        return os.path.join(data_dir, f"data0.txt")
    else:
        numbers = [int(re.match(r"data(\d+)\.txt", f).group(1)) for f in files]
        next_number = max(numbers) + 1
        return os.path.join(data_dir, f"data{next_number}.txt")
    
# The main function that runs whole program -> w/ baseline calculation
if __name__ == "__main__":
  data_buffer = [] 
  baseline_collected = False
  while True:
    output_file = get_next_filename(DATA_DIR)
    serial_data = read_serial_data(SERIAL_PORT, BAUD_RATE, SERIAL_TIMEOUT)
    if serial_data:
      for gsr_pair in serial_data:
        timestamp, gsr_value = gsr_pair
        data_buffer.append(gsr_pair) #Store data temporarily
        
        if not baseline_collected and len(data_buffer) >= BASELINE_COUNT:
          baseline_collected = calculate_baseline(data_buffer, BASELINE_COUNT)
          if not baseline_collected:
            data_buffer.pop(0) # Remove the first value to keep the buffer size constant
            continue

        if baseline_collected:
          output = process_data(float(gsr_value))
          if output is not None:
            with open(output_file, "a") as f:
              print(f"GSR Value: {gsr_value}, Baseline: {baseline_average} Output: {output}")
              f.write(f"{output}\n")
    else:
      print("No data received from serial.")
    time.sleep(READ_INTERVAL) # Wait for the next read interval
