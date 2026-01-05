import pyttsx3

engine = pyttsx3.init(driverName='sapi5')

engine.setProperty('rate', 170)   # speech speed
engine.setProperty('volume', 1.0) # max volume

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # default system voice

def speak(text):
    engine.say(text)
    engine.runAndWait()

