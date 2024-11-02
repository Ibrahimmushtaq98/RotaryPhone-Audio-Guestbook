import logging
import threading
import subprocess
import datetime
import time
import signal
import os
import configparser

from gpiozero import Device
from gpiozero import Button
from gpiozero.pins.rpigpio import RPiGPIOFactory
from signal import pause

class AudioGuesBookRotaryPhone:

    def __init__(self, config_file='config.ini'):
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Audio settings
        self.recording_limit = int(self.config['Audio']['recording_limit'])
        self.recording_format = self.config['Audio']['recording_format']
        self.recording_saved_filepath = self.config['Audio']['recording_saved_filepath']
        
        # Ensure the save directory exists
        os.makedirs(self.recording_saved_filepath, exist_ok=True)

        # GPIO settings for plunger detection
        self.PLUNGER_PIN = int(self.config['GPIO']['plunger_gpio'])
        self.plunger_isPulldown = self.config['GPIO'].getboolean('plunger_isPulldown')
        self.plunger_bounce_time = float(self.config['GPIO']['plunger_bounce_time'])

        # Set up the plunger button
        self.plunger = Button(self.PLUNGER_PIN, pull_up=not self.plunger_isPulldown, bounce_time=self.plunger_bounce_time)

        # State variable to manage recording process
        self.recording_process = None

        # Bind plunger events
        self.plunger.when_pressed = self.handset_lifted
        self.plunger.when_released = self.handset_down

        print("System initialized. Monitoring handset position for audio recording and playback.")

    # Generate a unique filename based on the current date and time
    def generate_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.recording_saved_filepath, f"REC_{timestamp}.wav")

    # Handset lifted - start recording
    def handset_lifted(self):
        recording_file = self.generate_filename()
        print(f"Handset is lifted. Starting recording to {recording_file}...")
        self.recording_process = subprocess.Popen([
            "arecord", "-f", self.recording_format, "-d", str(self.recording_limit), recording_file
        ])

    # Handset down - stop recording and playback
    def handset_down(self):
        if self.recording_process:
            self.recording_process.terminate()
            self.recording_process = None
            print("Handset is placed down. Stopping recording and playing back...")
            subprocess.run(["aplay", self.generate_filename()])

# Run the program
if __name__ == "__main__":
    phone_system = AudioGuesBookRotaryPhone()
    pause()  # Keep the program running to monitor plunger state

