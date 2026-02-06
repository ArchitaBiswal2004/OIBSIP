import os

print("Checking required files...\n")

required_files = [
    "run_server.py",
    "main.py",
    "requirements.txt",
    "server/__init__.py",
    "server/server.py",
    "server/database.py",
    "server/auth.py",
    "server/crypto.py",
    "client/__init__.py",
    "client/socket_client.py",
    "client/login_ui.py",
    "client/room_ui.py",
    "client/chat_ui.py"
]

missing = []
for file in required_files:
    if os.path.exists(file):
        print(f"✓ {file}")
    else:
        print(f"✗ {file} - MISSING!")
        missing.append(file)

print("\n" + "="*50)
if missing:
    print(f"Missing {len(missing)} file(s):")
    for f in missing:
        print(f"  - {f}")
else:
    print("All files present! Ready to run.")