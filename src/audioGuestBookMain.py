import os
import subprocess
import threading
from gpiozero import Button
from signal import pause
from datetime import datetime
import configparser
import time

import logging

# Set up logging
logging.basicConfig(
    filename='/home/rpi/RotaryPhone-Audio-Guestbook/logs/guestbook_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class SimplePhoneSystem:
    def __init__(self, config_file='config.ini'):
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Audio settings
        self.recording_format = self.config['Audio']['recording_format']
        self.recording_limit = int(self.config['Audio']['recording_limit'])
        self.recording_saved_filepath = self.config['Audio']['recording_saved_filepath']
        self.greeting_file = self.config['Audio']['greeting_file']  # Path to greeting message file

        # GPIO settings for plunger detection
        self.PLUNGER_PIN = int(self.config['GPIO']['plunger_gpio'])
        self.plunger_isPulldown = self.config['GPIO'].getboolean('plunger_isPulldown')
        self.plunger_bounce_time = float(self.config['GPIO']['plunger_bounce_time'])

        # Set up the plunger button
        self.plunger = Button(self.PLUNGER_PIN, pull_up=not self.plunger_isPulldown, bounce_time=self.plunger_bounce_time)

        # State variables to manage playback and recording processes
        self.handset_lifted_state = False
        self.greeting_thread = None
        self.recording_thread = None

        # Bind plunger events
        self.plunger.when_pressed = self.handle_handset_lifted
        self.plunger.when_released = self.handle_handset_down

        logging.info("System initialized. Monitoring handset position for audio recording and playback.")

    def generate_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.recording_saved_filepath, f"REC_{timestamp}.wav")

    def handle_handset_lifted(self):
        if not self.handset_lifted_state:
            self.handset_lifted_state = True
            logging.info("Handset lifted. Playing greeting message...")

            # Start a thread for the greeting
            self.greeting_thread = threading.Thread(target=self.play_greeting)
            self.greeting_thread.start()

    def handle_handset_down(self):
        if self.handset_lifted_state:
            self.handset_lifted_state = False
            logging.info("Handset placed down. Stopping any ongoing playback and recording.")

            # Stop the greeting and recording if they are running
            if self.greeting_thread and self.greeting_thread.is_alive():
                self.stop_greeting()
                self.greeting_thread.join()  # Ensure greeting thread has fully stopped
                self.greeting_thread = None

            if self.recording_thread and self.recording_thread.is_alive():
                self.stop_recording()
                self.recording_thread.join()  # Ensure recording thread has fully stopped
                self.recording_thread = None

    def play_greeting(self):
        # Play the greeting message
        greeting_process = subprocess.Popen(["aplay", self.greeting_file])
        greeting_process.wait()

        # Start recording only if the handset is still lifted after greeting finishes
        if self.handset_lifted_state:
            logging.info("Greeting finished. Starting recording...")
            self.recording_thread = threading.Thread(target=self.start_recording)
            self.recording_thread.start()

    def start_recording(self):
        # Set the microphone capture volume to 5%
        print("Setting microphone volume to 5%")
        subprocess.run(["amixer", "-c", "0", "set", "Mic", "5%"])
        
        # Record the audio message
        recording_file = self.generate_filename()
        self.recording_process = subprocess.Popen([
            "arecord", "-f", self.recording_format, "-d", str(self.recording_limit), recording_file
        ])
        self.recording_process.wait()

    def stop_recording(self):
        if self.recording_process and self.recording_process.poll() is None:
            self.recording_process.terminate()
            time.sleep(0.1)  # Short delay for graceful termination
            self.recording_process.wait()
            self.recording_process = None
            logging.info("Recording stopped.")

    def stop_recording(self):
        # Attempt to terminate the recording process if it's running
        logging.info("Stopping recording...")
        subprocess.run(["pkill", "-f", "arecord"])

# Run the program
if __name__ == "__main__":
    phone_system = SimplePhoneSystem()
    pause()  # Keep the program running to monitor plunger state
