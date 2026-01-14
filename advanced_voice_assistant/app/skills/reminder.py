import re
from datetime import datetime, timedelta
from app.core.state import get_state, require_slot, update_slot, clear_state
from app.core.scheduler import schedule_reminder, list_reminders, cancel_reminder

TIME_REGEX = re.compile(
    r'(\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)?',
    re.IGNORECASE
)

# -------------------- UTILITIES --------------------

def extract_task(command: str) -> str:
    command = command.lower()

    # Remove all reminder command prefixes
    command = re.sub(
        r"(set\s+)?remind(er)?\s+me\s+to|"
        r"(set\s+)?reminder\s+to|"
        r"(cancel|delete|remove)\s+reminder(\s+to|\s+for)?",
        "",
        command
    )

    # Remove time expressions
    command = re.sub(r"\s+at\s+.*", "", command)

    return command.strip()



def parse_time(command: str):
    match = TIME_REGEX.search(command)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    ampm = match.group(3)

    if ampm:
        ampm = ampm.replace(".", "").lower()

    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0

    now = datetime.now()
    reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if reminder_time <= now:
        reminder_time += timedelta(days=1)

    return reminder_time

# -------------------- SET REMINDER --------------------

def set_reminder(command: str):
    state = get_state()
    slots = state["slots"]

    if "task" not in slots:
        task = extract_task(command)
        if not task:
            require_slot("task")
            return "What should I remind you about?"
        update_slot("task", task)

    if "time" not in slots:
        time = parse_time(command)
        if not time:
            require_slot("time")
            return "At what time should I set the reminder?"
        update_slot("time", time)

    state = get_state()
    task = state["slots"]["task"]
    time = state["slots"]["time"]


    schedule_reminder(time, task)
    clear_state()

    return f"Reminder set for {task} at {time.strftime('%I:%M %p')}."

# -------------------- REMINDER MANAGEMENT --------------------

def handle_reminder_management(command: str):
    state = get_state()
    command = command.lower()

    # 🟡 HANDLE CANCEL SELECTION FIRST
    if state.get("pending_slot") == "cancel_choice":
        match = re.search(r"\d+", command)
        if not match:
            return "Please tell me the number of the reminder to cancel."

        index = int(match.group()) - 1
        options = state["slots"]["cancel_options"]

        if index < 0 or index >= len(options):
            return "That number is not valid."

        reminder = options[index]
        cancel_reminder(reminder["task"], reminder["time"])
        clear_state()

        return f"Reminder for {reminder['task']} at {reminder['time'].strftime('%I:%M %p')} has been cancelled."

    # 📋 LIST
    if "list" in command or "show" in command:
        clear_state()
        reminders = list_reminders()
        if not reminders:
            return "You have no active reminders."

        return "You have the following reminders: " + ", ".join(
            f"{r['task']} at {r['time'].strftime('%I:%M %p')}"
            for r in reminders
        )

    # ❌ CANCEL REMINDER
    if "cancel" in command or "delete" in command:
        task = extract_task(command)
        reminders = list_reminders()

        matches = [r for r in reminders if r["task"] == task]

    if not matches:
        return f"No reminder found for {task}."

    # ✅ SINGLE MATCH → cancel directly
    if len(matches) == 1:
        cancel_reminder(matches[0]["task"], matches[0]["time"])
        return (
            f"Reminder for {matches[0]['task']} at "
            f"{matches[0]['time'].strftime('%I:%M %p')} has been cancelled."
        )

    # 🔁 MULTIPLE MATCHES → ask user
    update_slot("cancel_options", matches)
    require_slot("cancel_choice")

    response = f"You have multiple reminders for {task}: "
    for i, r in enumerate(matches, start=1):
        response += f"{i}. {r['time'].strftime('%I:%M %p')} "
    response += "Please say first, second, or third."

    return response
