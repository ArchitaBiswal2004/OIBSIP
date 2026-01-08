import re
from datetime import datetime
from app.core.context import update_context

REMINDERS = []


def extract_time(command: str):
    """
    Extract time like:
    - 10 pm
    - 10:00 pm
    - 10:00 p.m.
    - 7:30 a.m.
    """
    time_pattern = r'(\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)'
    match = re.search(time_pattern, command, re.IGNORECASE)

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    meridian = match.group(3).replace(".", "").upper()

    if meridian == "PM" and hour != 12:
        hour += 12
    if meridian == "AM" and hour == 12:
        hour = 0

    return hour, minute


def clean_task(command: str):
    """
    Remove reminder phrases and time from task
    """
    task = re.sub(
        r"remind me to|remind me|at \d{1,2}(:\d{2})?\s*(a\.?m\.?|p\.?m\.?)",
        "",
        command,
        flags=re.IGNORECASE
    )
    return task.strip().capitalize()


def set_reminder(command: str):
    now = datetime.now()

    time_data = extract_time(command)

    if time_data:
        hour, minute = time_data
    else:
        # default: 5 minutes later (SMART default)
        hour = now.hour
        minute = (now.minute + 5) % 60

    reminder_time = now.replace(hour=hour, minute=minute, second=0)
    reminder_date = reminder_time.strftime("%Y-%m-%d")
    reminder_time_str = reminder_time.strftime("%I:%M %p")

    task = clean_task(command)

    REMINDERS.append({
        "task": task,
        "date": reminder_date,
        "time": reminder_time_str
    })

    update_context("last_reminder", task)

    return f"Reminder set for {reminder_time_str}: {task}"
