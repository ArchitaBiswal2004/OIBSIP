import requests

API_KEY = "YOUR_API_KEY"
CITY = "Bhubaneswar"

def get_weather(query):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]

    return f"The temperature in {CITY} is {temp} degrees Celsius with {desc}."
