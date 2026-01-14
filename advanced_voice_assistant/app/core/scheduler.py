import time
import threading
from datetime import datetime
from app.voice.speaker import speak

REMINDERS = []  # authoritative store


def schedule_reminder(reminder_time: datetime, task: str):
    REMINDERS.append({
        "time": reminder_time,
        "task": task,
        "triggered": False
    })


def list_reminders():
    return [
        r for r in REMINDERS
        if not r["triggered"]
    ]


def cancel_reminder(task: str | None = None):
    global REMINDERS

    if task is None:
        REMINDERS.clear()
        return "All reminders have been cancelled."

    for r in REMINDERS:
        if task.lower() in r["task"].lower():
            REMINDERS.remove(r)
            return f"I’ve cancelled your reminder to {r['task']}."

    return "I couldn't find that reminder."


def reminder_worker():
    while True:
        now = datetime.now()

        for reminder in REMINDERS:
            if not reminder["triggered"] and now >= reminder["time"]:
                speak(f"Reminder: {reminder['task']}")
                reminder["triggered"] = True

        time.sleep(1)


def start_scheduler():
    thread = threading.Thread(target=reminder_worker, daemon=True)
    thread.start()
