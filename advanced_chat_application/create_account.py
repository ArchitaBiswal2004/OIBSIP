

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.database import init_db, create_user
from server.auth import hash_password

def main():
    print("="*50)
    print("  Create Account Directly")
    print("="*50)
    
    init_db()
    
    username = input("\nEnter username (min 3 chars): ").strip()
    password = input("Enter password (min 6 chars): ")
    
    if len(username) < 3:
        print("❌ Username too short")
        return
    
    if len(password) < 6:
        print("❌ Password too short")
        return
    
    hashed = hash_password(password)
    
    if create_user(username, hashed):
        print(f"\n✅ Account created successfully!")
        print(f"Username: {username}")
        print(f"\nNow run: python main.py")
        print(f"And LOGIN with these credentials")
    else:
        print(f"\n❌ Username '{username}' already exists")

if __name__ == "__main__":
    main()