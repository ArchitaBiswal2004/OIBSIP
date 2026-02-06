#!/usr/bin/env python3
# run_server.py - Start the chat server

import sys
import os
from server.database import init_db
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.server import start_server


if __name__ == "__main__":
    print("=" * 50)
    print("  Advanced Chat Server")
    print("=" * 50)
    print()
    

# Force database recreation (remove this after first run)
    db_path = os.path.join(os.path.dirname(__file__), "server", "chat.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🔄 Old database removed, creating fresh one...")

    init_db()

    start_server()