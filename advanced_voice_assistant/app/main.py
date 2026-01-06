from app.voice.listener import listen
from app.voice.speaker import speak
from app.nlp.intent_parser import parse_intent

from app.skills.weather import get_weather
from app.skills.knowledge import get_knowledge
from app.skills.email import send_email
from app.skills.reminder import set_reminder

from app.core.context import update_context


def main():
    speak("Voice assistant is ready. Press Enter to speak.")

    while True:
        # Push-to-talk trigger
        input("\n▶ Press Enter to speak...")

        # Listen until silence
        command = listen()

        if not command:
            speak("I did not hear anything. Please try again.")
            continue

        # Detect intent
        intent = parse_intent(command)

        # Update conversation context
        update_context(intent, command)

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

        # Speak response
        speak(response)


if __name__ == "__main__":
    main()
