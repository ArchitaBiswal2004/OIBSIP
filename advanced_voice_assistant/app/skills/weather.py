import os
import re
import requests
from dotenv import load_dotenv
from app.core.context import update_context, get_context

load_dotenv()

# ==============================
# CONFIG
# ==============================
API_KEY = os.getenv("OPENWEATHER_API_KEY")

TIME_WORDS = ["today", "tomorrow", "now", "tonight", "next week"]
FILLER_PHRASES = [
    "what is", "what's", "tell me", "the weather",
    "weather", "temperature"
]


# ==============================
# UTILS
# ==============================
def normalize_command(command: str) -> str:
    command = command.lower().strip()

    for word in TIME_WORDS:
        command = command.replace(word, "")

    for phrase in FILLER_PHRASES:
        command = command.replace(phrase, "")

    return " ".join(command.split())


def get_current_city():
    """
    Detect user's city using IP location
    """
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        data = res.json()
        return data.get("city")
    except:
        return None


def extract_city(command: str):
    """
    Extract city name from user command
    """
    command = normalize_command(command)

    # Handle "my city"
    if "my city" in command or "my location" in command:
        return "CURRENT_LOCATION"

    # Priority 1: at/in <city>
    match = re.search(r"(?:at|in)\s+([a-zA-Z\s]{2,})$", command)
    if match:
        return match.group(1).strip()

    # Priority 2: <city> weather
    match = re.search(r"([a-zA-Z\s]{2,})$", command)
    if match:
        city = match.group(1).strip()
        if city not in ["at", "in"]:
            return city

    return None


# ==============================
# MAIN WEATHER FUNCTION
# ==============================
def get_weather(command: str):
    if not API_KEY:
        return "Weather service is not configured."

    # Tomorrow not implemented yet
    if "tomorrow" in command.lower():
        return "I can provide today's weather for now. Forecast support is coming soon."

    city = extract_city(command)

    # 🌍 Current location handling
    if city == "CURRENT_LOCATION":
        city = get_current_city()
        if not city:
            return "I couldn't determine your current city."

    # 🧠 Context fallback
    if not city:
        city = get_context("last_city")
        if not city:
            return "Please tell me the city name."

    # Save city in memory
    update_context("last_city", city)

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    try:
        res = requests.get(url, timeout=5)

        if res.status_code != 200:
            return f"I couldn't fetch the weather for {city.title()}."

        data = res.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"]

        return (
            f"The weather in {city.title()} today is {temp}°C "
            f"(feels like {feels_like}°C) with {desc}. "
            f"Humidity is {humidity}%."
        )

    except requests.exceptions.RequestException:
        return "Weather service is currently unavailable."
