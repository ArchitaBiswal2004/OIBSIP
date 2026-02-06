#!/usr/bin/env python3
# run_server.py - Start the chat server

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.server import start_server


if __name__ == "__main__":
    print("=" * 50)
    print("  Advanced Chat Server")
    print("=" * 50)
    print()

    start_server()