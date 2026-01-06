import re

def parse_intent(text):
    text = text.lower()

    if re.search(r'\b(exit|quit|bye|stop)\b', text):
        return "exit"

    if re.search(r'\b(weather|temperature|forecast)\b', text):
        return "weather"

    if re.search(r'\b(remind|remember|alert)\b', text):
        return "reminder"

    if re.search(r'\b(email|mail|send email)\b', text):
        return "email"

    return "knowledge"




