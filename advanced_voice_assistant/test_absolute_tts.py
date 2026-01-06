import pyttsx3
import time

engine = pyttsx3.init(driverName="sapi5")
engine.setProperty("rate", 170)

voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)

print("SPEAKING NOW...")
engine.say("This is a direct test. You should hear my voice.")
engine.runAndWait()

time.sleep(1)
print("DONE")
