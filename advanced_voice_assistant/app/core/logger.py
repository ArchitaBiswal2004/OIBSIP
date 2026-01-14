import logging
from datetime import datetime



# Only WARN logs should be printed


def log(level: str, message: str):
    if level == "WARN":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [WARN] {message}")


logging.basicConfig(
    filename="assistant.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)