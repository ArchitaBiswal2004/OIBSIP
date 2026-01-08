# app/core/scheduler.py
import time
import threading
from datetime import datetime
from app.voice.speaker import speak
from app.skills.reminder import REMINDERS

def reminder_worker():
    while True:
        now = datetime.now()

        for reminder in REMINDERS[:]:  # copy to avoid mutation issues
            try:
                reminder_time = datetime.strptime(
                    f"{reminder['date']} {reminder['time']}",
                    "%Y-%m-%d %I:%M %p"
                )

                if now >= reminder_time:
                    speak(f"Reminder: {reminder['task']}")
                    REMINDERS.remove(reminder)
            except Exception as e:
                print("Error processing reminder:", e)

        time.sleep(1)

def start_scheduler():
    thread = threading.Thread(target=reminder_worker, daemon=True)
    thread.start()
