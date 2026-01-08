"""
Context manager for the voice assistant.
Stores short-term conversation memory.
"""

# Internal context storage (session-based)
_context = {}


def update_context(key: str, value):
    """
    Store or update a context value.
    Example: update_context("last_city", "Delhi")
    """
    if not key:
        return

    _context[key] = value


def get_context(key: str, default=None):
    """
    Retrieve a value from context.
    Example: get_context("last_city")
    """
    return _context.get(key, default)


def clear_context():
    """
    Clear all stored context.
    Useful on 'exit' or reset.
    """
    _context.clear()
