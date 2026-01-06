from app.skills.weather import get_weather
from app.skills.email import send_email
from app.skills.knowledge import answer_question
from app.voice.speaker import speak


def route(intent, command):
    if intent == "weather":
        speak(get_weather())

    elif intent == "email":
        speak(send_email())

    elif intent == "knowledge":
        response = answer_question(command)
        speak(response)

    elif intent == "exit":
        speak("Goodbye!")
        exit()

    else:
        speak("Sorry, I did not understand that.")
