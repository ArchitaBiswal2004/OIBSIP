from app.core.context import get_context

def parse_intent(command: str):
    command = command.lower().strip()

    if any(w in command for w in ["exit", "quit", "bye"]):
        return "exit"

    if any(w in command for w in ["weather", "temperature", "forecast"]):
        return "weather"

    # 🔥 FOLLOW-UP HANDLING
    if any(w in command for w in ["tomorrow", "today"]):
        last_intent = get_context("last_intent")
        if last_intent:
            return last_intent

    if any(w in command for w in ["who is", "what is", "tell me about"]):
        return "knowledge"

    if "email" in command:
        return "email"

    if any(word in command for word in ["remind", "reminder"]):
        return "reminder"


    return "unknown"
