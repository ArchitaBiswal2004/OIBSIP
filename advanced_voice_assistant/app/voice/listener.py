import speech_recognition as sr

recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    # 🔴 mic released HERE (after with-block)

    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣 You said: {text}")
        return text.lower()
    except:
        return ""
