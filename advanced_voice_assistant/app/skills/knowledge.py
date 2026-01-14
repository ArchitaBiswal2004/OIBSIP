"""
Knowledge skill for the voice assistant.
Uses Wikipedia as a trusted knowledge source.
"""

import re
import wikipediaapi
from app.core.context import update_context, get_context

# ✅ REQUIRED: user_agent
wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="AdvancedVoiceAssistant/1.0 (OIBSIP Internship Project)",
    extract_format=wikipediaapi.ExtractFormat.WIKI
)


def extract_entity(command: str):
    """
    Extract entity from questions like:
    - who is Elon Musk
    - what is NASA
    - tell me about India
    """
    command = command.lower().strip()

    patterns = [
        r"who is (.+)",
        r"what is (.+)",
        r"tell me about (.+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            return match.group(1).strip()

    return None


def get_knowledge(command: str):
    # Extract entity
    entity = extract_entity(command)

    # Follow-up support
    if not entity:
        entity = get_context("last_entity")

    if not entity:
        return "Please tell me what or who you want to know about."

    # Store entity for follow-ups
    update_context("last_entity", entity)

    # Wikipedia lookup
    page = wiki.page(entity)

    if not page.exists():
        return f"Sorry, I could not find reliable information on {entity}."

    summary = page.summary.strip()

    if not summary:
        return f"I found {entity}, but there is not enough information to summarize."

    # Speakable summary (2 sentences max)
    sentences = summary.split(". ")
    short_summary = ". ".join(sentences[:2]).strip()

    return short_summary + "."
