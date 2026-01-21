# 🎙️ Advanced Voice Assistant

An AI-powered voice assistant built using Python that supports natural language interaction, task automation, and reminder management.

---

## 🚀 Features

- 🎤 Speech recognition and voice output
- ⏰ Advanced reminder management
  - Set reminders with time
  - List reminders
  - Cancel specific reminders
  - Handles multiple reminders for the same task
- 🌦️ Weather updates
- 🧠 Knowledge-based Q&A
- 📧 Email automation via voice
- 🧩 Context-aware intent handling

---

## 🛠️ Tech Stack

- Python
- SpeechRecognition
- pyttsx3
- NLP-based intent parsing
- Threading & scheduling
- Modular architecture

---

## 📂 Project Structure

```text
app/
 ├── core/        # Scheduler, state, logging
 ├── nlp/         # Intent parsing
 ├── skills/      # Assistant capabilities
 ├── voice/       # Speech input/output
 └── main.py

## How to run
python -m app.main
