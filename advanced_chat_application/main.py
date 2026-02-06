#!/usr/bin/env python3
# main.py - Start the chat client

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.login_ui import LoginWindow

if __name__ == "__main__":
    print("=" * 50)
    print("  Advanced Chat Client")
    print("=" * 50)
    print()
    
    # Start the login window
    LoginWindow(host="127.0.0.1", port=5555)