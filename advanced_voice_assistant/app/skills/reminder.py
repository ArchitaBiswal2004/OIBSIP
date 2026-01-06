import threading
import time
from app.voice.speaker import speak

def set_reminder(command):
    def reminder_task():
        time.sleep(10)
        speak("This is your reminder.")

    threading.Thread(target=reminder_task, daemon=True).start()
    return "Reminder set for ten seconds from now."
