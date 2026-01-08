from app.voice.listener import listen
from app.voice.speaker import speak
from app.nlp.intent_parser import parse_intent
from app.core.context import update_context
from app.skills.weather import get_weather
from app.skills.knowledge import get_knowledge
from app.skills.email import send_email
from app.skills.reminder import set_reminder
from app.core.logger import log
from app.core.scheduler import start_scheduler



def main():
    start_scheduler()  # start background reminders
    speak("Voice assistant is ready. Press Enter to speak.")

    while True:
        # Push-to-talk
        input("\n▶ Press Enter to speak...")

        # Listen until silence
        command = listen()

        if not command:
            speak("I did not hear anything. Please try again.")
            continue

        # Detect intent
        intent = parse_intent(command)

        # ✅ Store conversational context (CRITICAL)
        update_context("last_intent", intent)
        update_context("last_command", command)

        # Log interaction
        log(f"Command: {command} | Intent: {intent}")

        # Route to skills
        if intent == "weather":
            response = get_weather(command)

        elif intent == "knowledge":
            response = get_knowledge(command)

        elif intent == "email":
            response = send_email(command)

        elif intent == "reminder":
            response = set_reminder(command)

        elif intent == "exit":
            speak("Goodbye!")
            break

        else:
            response = "Sorry, I did not understand that."

        speak(response)


if __name__ == "__main__":
    main()
