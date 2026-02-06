# server/auth.py
import bcrypt
import uuid
from server.database import create_user, get_user, create_session, validate_session, update_last_seen


def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), hashed)


def register_user(username, password):
    """
    Register a new user
    Returns: (success: bool, message: str, session: str or None)
    """
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters", None

    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters", None

    # Check for invalid characters
    if not username.replace("_", "").replace("-", "").isalnum():
        return False, "Username can only contain letters, numbers, _ and -", None

    hashed = hash_password(password)

    if create_user(username, hashed):
        # Auto-login after registration
        session_id = str(uuid.uuid4())
        create_session(session_id, username)
        return True, "Registration successful", session_id
    else:
        return False, "Username already taken", None


def login_user(username, password):
    """
    Authenticate a user
    Returns: (success: bool, message: str, session: str or None)
    """
    user = get_user(username)

    if not user:
        return False, "Invalid username or password", None

    stored_hash = user["password_hash"]

    if not verify_password(password, stored_hash):
        return False, "Invalid username or password", None

    # Update last seen
    update_last_seen(username)

    # Create session
    session_id = str(uuid.uuid4())
    create_session(session_id, username)

    return True, "Login successful", session_id


def authenticate_session(session_id):
    """
    Validate a session and return username
    Returns: username or None
    """
    if not session_id:
        return None

    username = validate_session(session_id)
    if username:
        update_last_seen(username)

    return username


def require_auth(func):
    """Decorator to require authentication for handler functions"""
    def wrapper(conn, data, *args, **kwargs):
        session = data.get("session")
        username = authenticate_session(session)

        if not username:
            conn.send({"ok": False, "msg": "Authentication required"})
            return

        data["authenticated_user"] = username
        return func(conn, data, *args, **kwargs)

    return wrapper