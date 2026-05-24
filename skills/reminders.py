"""
Time and reminders skill.
Reminders use macOS Notification Center via AppleScript.
"""

import subprocess
from datetime import datetime
import threading


def get_time() -> str:
    """Return current date and time."""
    now = datetime.now()
    return now.strftime("It's %I:%M %p on %A, %B %d, %Y.")


def set_reminder(message: str, minutes: int) -> str:
    """
    Set a reminder using macOS notification via AppleScript.
    Fires after `minutes` minutes.
    """
    def _fire_reminder():
        script = f'''
        display notification "{message}" with title "JARVIS Reminder" sound name "Glass"
        '''
        subprocess.run(["osascript", "-e", script])

    timer = threading.Timer(minutes * 60, _fire_reminder)
    timer.daemon = True
    timer.start()

    if minutes == 1:
        return f"Reminder set. I'll notify you in 1 minute about: {message}"
    return f"Reminder set. I'll notify you in {minutes} minutes about: {message}"
