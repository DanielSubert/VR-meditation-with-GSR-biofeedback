from board import GP20, GP21, A1
from analogio import AnalogIn
from time import monotonic as now
from digitalio import DigitalInOut, Direction, Pull
import usb_cdc
import time
# Constants
DEBOUNCE_DELAY = 0.05
BUFFER_SIZE = 500
PRINT_INTERVAL = 3
class Buffer:
    def __init__(self, factor=500):
        self.factor = factor
        self.buffer = []
        self.total = 0
    def put(self, measure):
        self.buffer.append(measure)
        self.total += measure
        if len(self.buffer) > self.factor:
            self.total -= self.buffer.pop(0)
    def poll(self):
        if len(self.buffer) >= self.factor:
            return self.total / len(self.buffer)
        return None
    def clear(self):
        self.buffer.clear()
        self.total = 0
class Button:
    def __init__(self, pin, debounce_time=0.2):
        self.button = DigitalInOut(pin)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.UP
        self.last_state = self.button.value
        self.last_time = now()
        self.debounce_time = debounce_time
        self.state = False
    def update_state(self):
        current_time = now()
        if current_time - self.last_time >= self.debounce_time:
            current_state = self.button.value
            if current_state != self.last_state:
                self.last_time = current_time
                self.last_state = current_state
                self.state = not current_state  # Button is pressed(active-low)
    def get_state(self):
        return self.state
    def reset(self):
        self.state = False
class Sensor:
    def __init__(self, pin):
        self.sensor = AnalogIn(pin)
    def read_value(self):
        return self.sensor.value

class RecordingFunction:
    def __init__(self):
        self.state = "Idle"
        self.btn_start_stop = Button(GP20)
        self.btn_pause_resume = Button(GP21)
        self.sensor = Sensor(A1)
        self.buffer = Buffer(BUFFER_SIZE)
        self.last_print_time = 0
        self.recording = False
        self.recording_paused = False
        
    def idle_state(self):
        if self.btn_start_stop.get_state():
           # print(f"{now():.3f} Starting recording...")
            self.state = "Default"
            self.recording = True
            self.recording_paused = False
            self.btn_start_stop.reset()
 
    def default_state(self):
        gsr_value = self.sensor.read_value()
        self.buffer.put(gsr_value)
        average_value = self.buffer.poll()
        if average_value is not None and now() - self.last_print_time > PRINT_INTERVAL:
            self.last_print_time = now()
            print(f"{now():.3f}, {average_value}")  # Print withtimestamp
            message = f"{now():.3f}, {average_value}\n"
            try:
                if usb_cdc.data:
                    usb_cdc.data.write(message.encode('utf-8'))
                    time.sleep(0.1) #Added delay
            except Exception as e:
                print(f"Error writing to serial:{e}")
       # if self.btn_start_stop.get_state():
        #    print(f"{now():.3f} Stopping recording...")
        #    self.state = "Idle"
         #   self.recording = False
          #  self.btn_start_stop.reset()
      #  elif self.btn_pause_resume.get_state():
        #    print(f"{now():.3f} Pausing recording...")
       #     self.state = "Paused"
        #    self.recording_paused = True
         #   self.btn_pause_resume.reset() #Resume button state
    def paused_state(self):
        pass
   #     if self.btn_pause_resume.get_state():
    #        #    print(f"{now():.3f} Resuming recording...")
     #       self.state = "Default"
      #      self.recording_paused = False
       #     self.btn_pause_resume.reset()
        #elif self.btn_start_stop.get_state():
         #   print(f"{now():.3f} Restarting recording...")
          #  self.buffer.clear()
           # self.state = "Default"
            #self.recording_paused = False
            #self.btn_start_stop.reset()
    
    def update(self):
        self.btn_start_stop.update_state()
        self.btn_pause_resume.update_state()
        if self.state == "Idle":
            self.idle_state()
        elif self.state == "Default":
            self.default_state()
        elif self.state == "Paused":
            self.paused_state()

 
def main():
    state_program = RecordingFunction()
    while True:
        state_program.update()
        time.sleep(0.01)  # Small delay
if __name__ == "__main__":
   main()