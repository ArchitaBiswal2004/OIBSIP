def parse_intent(text: str) -> str:
    text = text.lower()

    if any(w in text for w in ["exit", "quit", "bye"]):
        return "exit"

    # 🔥 REMINDER MANAGEMENT (expanded)
    if (
        "list" in text and "reminder" in text
        or "show reminder" in text
        or "show me the reminder" in text
        or "reminder list" in text
        or "delete reminder" in text
        or "cancel reminder" in text
        or "remove reminder" in text
    ):
        return "reminder_manage"

    # REMINDER SET
    if "remind" in text or "reminder" in text:
        return "reminder"

    if "weather" in text:
        return "weather"

    if "email" in text:
        return "email"

    if any(w in text for w in ["who is", "what is"]):
        return "knowledge"

    return "unknown"
