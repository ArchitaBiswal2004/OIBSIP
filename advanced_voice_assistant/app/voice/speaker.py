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

"""
# app/voice/speaker.py
import pyttsx3
import threading
import queue

_speech_queue = queue.Queue()
engine = pyttsx3.init(driverName="sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 175)

def _worker():
    while True:
        text = _speech_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()
        _speech_queue.task_done()

_thread = threading.Thread(target=_worker, daemon=True)
_thread.start()

def speak(text: str):
    """"""Queue text for speaking""""""
    if text:
        print(f"🔊 Speaking: {text}")
        _speech_queue.put(text)"""
