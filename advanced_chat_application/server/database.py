import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "chat.db")


@contextmanager
def get_db():
    """Context manager for database ***s"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database with all required tables"""
    with get_db() as conn:
        cur = conn.cursor()
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Messages table with enhanced features
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                room TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                edited_at TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                reply_to TEXT,
                FOREIGN KEY (sender) REFERENCES users(username)
            )
        """)
        
        # Read receipts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS read_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                username TEXT NOT NULL,
                read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(message_id, username),
                FOREIGN KEY (message_id) REFERENCES messages(message_id),
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        
        # Typing indicators table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS typing_status (
                room TEXT NOT NULL,
                username TEXT NOT NULL,
                last_typed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (room, username)
            )
        """)
        
        # Media attachments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_data BLOB NOT NULL,
                file_size INTEGER NOT NULL,
                FOREIGN KEY (message_id) REFERENCES messages(message_id)
            )
        """)
        
        # Sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        
        conn.commit()
        print("✅ Database initialized successfully")


def create_user(username, password_hash):
    """Create a new user"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def get_user(username):
    """Get user by username"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT username, password_hash FROM users WHERE username = ?",
            (username,)
        )
        return cur.fetchone()


def update_last_seen(username):
    """Update user's last seen timestamp"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET last_seen = ? WHERE username = ?",
            (datetime.now(), username)
        )
        conn.commit()


def save_message(room, sender, message, message_id, reply_to=None):
    """Save a message to the database"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO messages (message_id, room, sender, message, reply_to)
            VALUES (?, ?, ?, ?, ?)
        """, (message_id, room, sender, message, reply_to))
        conn.commit()


def fetch_room_history(room, limit=100):
    """Fetch recent messages from a room"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT sender, message, message_id, 
                   strftime('%H:%M', timestamp) as time,
                   reply_to, edited_at
            FROM messages
            WHERE room = ? AND is_deleted = 0
            ORDER BY timestamp DESC
            LIMIT ?
        """, (room, limit))
        return list(reversed(cur.fetchall()))


def delete_message(message_id):
    """Soft delete a message"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE messages SET is_deleted = 1 WHERE message_id = ?",
            (message_id,)
        )
        conn.commit()


def edit_message(message_id, new_text):
    """Edit an existing message"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE messages 
            SET message = ?, edited_at = ?
            WHERE message_id = ?
        """, (new_text, datetime.now(), message_id))
        conn.commit()


def clear_room(room):
    """Clear all messages in a room"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE messages SET is_deleted = 1 WHERE room = ?",
            (room,)
        )
        conn.commit()


def mark_message_read(message_id, username):
    """Mark a message as read by a user"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO read_receipts (message_id, username)
                VALUES (?, ?)
            """, (message_id, username))
            conn.commit()
    except sqlite3.IntegrityError:
        pass  # Already marked as read


def get_read_receipts(message_id):
    """Get all users who read a message"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT username, read_at
            FROM read_receipts
            WHERE message_id = ?
        """, (message_id,))
        return cur.fetchall()


def update_typing_status(room, username):
    """Update typing indicator for user in room"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO typing_status (room, username, last_typed)
            VALUES (?, ?, ?)
        """, (room, username, datetime.now()))
        conn.commit()


def get_typing_users(room):
    """Get users currently typing in a room (within last 3 seconds)"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT username
            FROM typing_status
            WHERE room = ?
            AND datetime(last_typed) > datetime('now', '-3 seconds')
        """, (room,))
        return [row[0] for row in cur.fetchall()]


def save_attachment(message_id, filename, file_type, file_data):
    """Save file attachment"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO attachments (message_id, filename, file_type, file_data, file_size)
            VALUES (?, ?, ?, ?, ?)
        """, (message_id, filename, file_type, file_data, len(file_data)))
        conn.commit()


def get_attachment(message_id):
    """Get attachment for a message"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT filename, file_type, file_data, file_size
            FROM attachments
            WHERE message_id = ?
        """, (message_id,))
        return cur.fetchone()


def create_session(session_id, username, expires_in_hours=24):
    """Create user session"""
    from datetime import timedelta
    expires_at = datetime.now() + timedelta(hours=expires_in_hours)
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sessions (session_id, username, expires_at)
            VALUES (?, ?, ?)
        """, (session_id, username, expires_at))
        conn.commit()


def validate_session(session_id):
    """Validate and return username for session"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT username
            FROM sessions
            WHERE session_id = ?
            AND datetime(expires_at) > datetime('now')
        """, (session_id,))
        result = cur.fetchone()
        return result[0] if result else None


def delete_session(session_id):
    """Delete a session (logout)""" 
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()