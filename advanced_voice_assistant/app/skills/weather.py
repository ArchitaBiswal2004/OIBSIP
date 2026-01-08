import os
import requests
from dotenv import load_dotenv
from app.core.context import update_context, get_context
import re
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")



def extract_city(command: str):
    command = command.lower()

    # Remove time-related noise
    noise_words = ["today", "tomorrow", "now", "please"]
    for word in noise_words:
        command = command.replace(word, "")

    patterns = [
        r"weather (in|at) ([a-z\s]+)",
        r"(in|at) ([a-z\s]+)",
        r"([a-z\s]+) weather"
    ]

    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            city = match.group(match.lastindex).strip()

            # Basic validation
            if 3 <= len(city) <= 25:
                return city

    return None



def get_weather(command: str):
    if not API_KEY:
        return "Weather service is not configured."
    
    if "tomorrow" in command.lower():
        return "Tomorrow's forecast is coming soon. I can tell you today's weather for now."


    # Try extracting city from command
    city = extract_city(command)

    # If city not spoken, use context
    if not city:
        city = get_context("last_city")

        if not city:
            return "Please tell me the city name."

    # Store city in context
    update_context("last_city", city)

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    try:
        res = requests.get(url, timeout=5)

        if res.status_code != 200:
            return f"I couldn't fetch the weather for {city}."

        data = res.json()

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]

        return f"The weather in {city.title()} today is {temp} degrees Celsius with {desc}."

    except requests.exceptions.RequestException:
        return "Weather service is currently unavailable."
