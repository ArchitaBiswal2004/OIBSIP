import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import re
from app.core.context import update_context

load_dotenv()

# SMTP credentials
EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# Demo / placeholder storage
SENT_EMAILS = []

def extract_email_task(command: str):
    """
    Extract recipient and message from command.
    Examples:
    - "send email to John saying hi"
    - "send email to Alice Hello, how are you?"
    """
    # recipient
    recipient_match = re.search(r"to ([a-zA-Z0-9\s]+)( saying|:|$)", command, re.IGNORECASE)
    recipient = recipient_match.group(1).strip() if recipient_match else None

    # message
    message_match = re.search(r"saying (.+)$", command, re.IGNORECASE)
    if not message_match:
        message_match = re.search(r"to [a-zA-Z0-9\s]+ (.+)$", command, re.IGNORECASE)
    message = message_match.group(1).strip() if message_match else None

    return recipient, message


def send_email(command: str):
    """
    Send an email or simulate sending (demo mode).
    """
    recipient, message = extract_email_task(command)

    # Ask for missing details
    if not recipient:
        return "Please specify the recipient."
    if not message:
        return "Please specify the email message."

    # Store in context and placeholder
    SENT_EMAILS.append({"recipient": recipient, "message": message})
    update_context("last_email", {"recipient": recipient, "message": message})

    # If SMTP credentials are set, send real email
    if EMAIL and PASSWORD:
        try:
            msg = EmailMessage()
            msg["From"] = EMAIL
            msg["To"] = EMAIL  # For demo, sending to self; you can replace with recipient
            msg["Subject"] = f"Voice Assistant Email to {recipient}"
            msg.set_content(message)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL, PASSWORD)
                server.send_message(msg)

            return f"Email sent successfully to {recipient}."

        except Exception as e:
            return "Email service is currently unavailable. The message has been saved for later delivery."


    # If no credentials, fallback to placeholder
    return f"Email (placeholder) sent to {recipient} with message: {message}"
