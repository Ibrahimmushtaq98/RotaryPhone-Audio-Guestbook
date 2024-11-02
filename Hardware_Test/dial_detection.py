from gpiozero import Button
from signal import pause
import time

# Define the GPIO pins
DIAL_STATUS_PIN = 5  # Pin connected to the white wires (dial open/close switch)
PULSE_PIN = 6        # Pin connected to the green pulse wire

# Set up the buttons with debounce for stable detection
dial_status = Button(DIAL_STATUS_PIN, pull_up=False, bounce_time=0.01)  # Slightly longer debounce
pulse_detector = Button(PULSE_PIN, pull_up=False, bounce_time=0.01)     # Increase bounce time for pulses

pulse_count = 0
dialing = False
last_pulse_time = time.time()

# Callback function to handle pulse counting
def pulse_detected():
    global pulse_count, last_pulse_time
    current_time = time.time()
    
    # Ignore pulses that happen too close together (e.g., within 30ms)
    if current_time - last_pulse_time > 0.03:  # 30 ms between pulses
        pulse_count += 1
        last_pulse_time = current_time
        print(f"Pulse detected! Total pulses: {pulse_count}")

# Function to handle the start of dialing
def start_dialing():
    global dialing, pulse_count
    if not dialing:
        dialing = True
        pulse_count = 0  # Reset pulse count at the start of each dial
        print("Dial is spinning...")

# Function to handle the end of dialing
def end_dialing():
    global dialing, pulse_count
    if dialing:
        dialing = False
        time.sleep(0.2)  # Wait briefly to ensure no more pulses come in
        print(f"Number dialed: {pulse_count}")
        pulse_count = 0  # Reset pulse count after each number is printed

# Bind the pulse counting to each falling edge on the pulse pin
pulse_detector.when_pressed = pulse_detected  # Trigger on each pulse detected

# Bind the start and end of dialing to the dial status pin
dial_status.when_pressed = end_dialing    # Called when dial stops spinning
dial_status.when_released = start_dialing  # Called when dial starts spinning

print("Ready to detect dial rotation and numbers dialed.")
pause()  # Keep the program running to detect events
