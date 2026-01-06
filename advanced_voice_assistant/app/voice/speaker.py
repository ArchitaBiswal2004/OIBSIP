import pyttsx3
import time

def speak(text: str):
    if not text:
        return

    # 🔴 REQUIRED: give microphone time to release audio device
    time.sleep(0.6)

    print(f"🔊 Speaking: {text}")

    engine = pyttsx3.init(driverName="sapi5")
    engine.setProperty("rate", 170)

    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)

    engine.say(text)
    engine.runAndWait()

    engine.stop()
    del engine
