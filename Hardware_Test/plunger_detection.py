from gpiozero import Button
from signal import pause

# Define the GPIO pin for the plunger
plunger = Button(26, pull_up=False, bounce_time=0.2)  # Set pull_up=False for a pull-down resistor behavior

# Function to check if the handset is off the stand (button pressed) or on the stand (button released)
def handset_lifted():
    print("Handset is off the stand (lifted).")

def handset_down():
    print("Handset is on the stand.")

# Bind the functions to the handset state
plunger.when_pressed = handset_lifted  # When circuit is closed (handset lifted)
plunger.when_released = handset_down   # When circuit is open (handset down)

# Wait indefinitely for button presses/releases
print("Monitoring handset position. Press CTRL+C to exit.")
pause()
