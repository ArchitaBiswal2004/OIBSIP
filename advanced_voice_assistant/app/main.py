from app.voice.listener import listen
from app.voice.speaker import speak
from app.nlp.intent_parser import parse_intent

from app.core.context import update_context
from app.core.logger import log
from app.core.scheduler import start_scheduler
from app.core.state import (
    get_state,
    start_intent,
    clear_state,
    require_slot
)

from app.skills.weather import get_weather
from app.skills.knowledge import get_knowledge
from app.skills.email import send_email
from app.skills.reminder import set_reminder, handle_reminder_management


def main():
    start_scheduler()
    speak("Voice assistant is ready. Press Enter to speak.")

    while True:
        response = None

        input("\n▶ Press Enter to speak...")
        command = listen()

        if not command:
            speak("I did not hear anything. Please try again.")
            log("WARN", "No speech detected")
            continue

        update_context("last_command", command)

        state = get_state()

        # 🔍 Intent detection
        intent = parse_intent(command)
        update_context("last_intent", intent)

        # 🔁 REMINDER SLOT FILLING (STRICT)
        if state.get("pending_slot"):
            if intent != "reminder":
                clear_state()
            else:
                response = set_reminder(command)
                if response:
                    speak(response)
                continue

        # ▶ Start new intent
        start_intent(intent)

        # 🌦 WEATHER
        if intent == "weather":
            response = get_weather(command)
            if response == "Please tell me the city name.":
                require_slot("city")

        # 🧠 KNOWLEDGE
        elif intent == "knowledge":
            response = get_knowledge(command)

        # 📧 EMAIL
        elif intent == "email":
            response = send_email(command)

        # ⏰ REMINDER
        elif intent == "reminder":
            response = set_reminder(command)

        # 🧾 REMINDER MANAGEMENT
        elif intent == "reminder_manage":
            response = handle_reminder_management(command)

        # ❌ EXIT
        elif intent == "exit":
            speak("Goodbye!")
            break

        # ❓ TRUE FALLBACK (ONLY HERE)
        else:
            response = "Sorry, I did not understand that."
            log("WARN", "Unknown intent")

        if response:
            speak(response)

        if response and response.startswith("Reminder set for"):
            clear_state()


if __name__ == "__main__":
    main()
