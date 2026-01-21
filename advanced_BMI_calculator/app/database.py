import sqlite3
from datetime import datetime
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "bmi_data.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            bmi REAL NOT NULL,
            category TEXT NOT NULL,
            health_risk TEXT NOT NULL,
            insight TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_bmi_record(username, weight, height, bmi, category, health_risk, insight):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bmi_records
        (username, weight, height, bmi, category, health_risk, insight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, weight, height, bmi, category, health_risk, insight))

    conn.commit()
    conn.close()


def fetch_user_history(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bmi, category, health_risk, insight, timestamp
        FROM bmi_records
        WHERE username = ?
        ORDER BY timestamp
    """, (username,))

    records = cursor.fetchall()
    conn.close()
    return records


