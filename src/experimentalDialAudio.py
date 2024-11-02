import os
import subprocess
import threading
from gpiozero import Button
from signal import pause
from datetime import datetime
import configparser
import time

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

        # Sound mappings for dial codes
        self.sounds = self.load_sound_mappings()

        # GPIO settings for plunger and dial detection
        self.PLUNGER_PIN = int(self.config['GPIO']['plunger_gpio'])
        self.plunger_isPulldown = self.config['GPIO'].getboolean('plunger_isPulldown')
        self.plunger_bounce_time = float(self.config['GPIO']['plunger_bounce_time'])

        # Set up the plunger button
        self.plunger = Button(self.PLUNGER_PIN, pull_up=not self.plunger_isPulldown, bounce_time=self.plunger_bounce_time)

        # State variables
        self.handset_lifted_state = False
        self.activated = False  # Indicates if the system is ready for a dial code
        self.dialed_code = None

        # Bind plunger events
        self.plunger.when_pressed = self.handle_handset_lifted
        self.plunger.when_released = self.handle_handset_down

        print("System initialized. Monitoring handset position and dial activity.")

    def load_sound_mappings(self):
        """Load sound mappings from the configuration file."""
        sounds = {}
        if 'Sounds' in self.config:
            for key, path in self.config['Sounds'].items():
                sounds[key] = path
        return sounds

    def handle_handset_lifted(self):
        if self.activated:
            # Handset is lifted and system is activated, so wait for a dial code
            print("Handset lifted. Waiting for a dial code.")
            self.dialed_code = None  # Reset any previous dial code

    def handle_handset_down(self):
        if self.activated and self.dialed_code:
            # Play the sound associated with the dialed code
            sound_file = self.sounds.get(self.dialed_code)
            if sound_file:
                print(f"Playing sound for dialed code: {self.dialed_code}")
                subprocess.run(["aplay", sound_file])
            else:
                print(f"No sound associated with dialed code: {self.dialed_code}")

        # Reset system on handset down
        self.activated = False
        self.dialed_code = None
        print("System reset. Place the handset back to activate dialing.")

    def handle_dial(self, number):
        if not self.handset_lifted_state:
            # If handset is on the base, check for activation
            if number == "1":
                self.activated = True
                print("Dialed '1' with handset on the base. System activated.")
        elif self.activated:
            # Accept a single dial code after activation
            if self.dialed_code is None:
                self.dialed_code = number
                print(f"Dial code accepted: {self.dialed_code}")
            else:
                # If more than one number is dialed, ignore
                print("Ignored additional dial input.")

# Run the program
if __name__ == "__main__":
    phone_system = SimplePhoneSystem()
    pause()  # Keep the program running to monitor plunger state
