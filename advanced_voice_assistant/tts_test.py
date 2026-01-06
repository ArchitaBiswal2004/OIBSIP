import time
import pyttsx3

time.sleep(1)
engine = pyttsx3.init(driverName="sapi5")
engine.say("If you hear this, TTS is working perfectly")
engine.runAndWait()
