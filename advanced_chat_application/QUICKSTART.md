# Quick Start Guide 🚀

## Installation (One-time setup)

```bash
# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Step 1: Start the Server
Open a terminal and run:
```bash
python run_server.py
```

You should see:
```
==================================================
  Advanced Chat Server
==================================================

✅ Database initialized successfully
✅ Server running on 0.0.0.0:5555
Waiting for ***s...
```

### Step 2: Start Client(s)
Open a **new terminal** (keep server running) and run:
```bash
python main.py
```

### Step 3: Register/Login
1. Enter a username (min 3 characters)
2. Enter a password (min 6 characters)
3. Click "Register" for new account or "Login" for existing

### Step 4: Join a Room
1. Enter a room name (e.g., "general", "work", "gaming")
2. Or click one of the popular room buttons
3. Click "Join Room"

### Step 5: Start Chatting! 💬
- Type your message and click "Send" or press Ctrl+Enter
- Click 📎 to attach files
- Right-click messages for more options (reply, edit, delete)
- See typing indicators when others are typing
- Get read receipts when messages are read

## Testing with Multiple Users

To simulate multiple users:

1. Keep the server running
2. Open multiple terminals
3. Run `python main.py` in each terminal
4. Register different users in each window
5. Join the same room and start chatting!

## Keyboard Shortcuts

- **Ctrl+Enter**: Send message
- **Right-click**: Message options menu
- **Enter**: Submit forms (login, room selection)

## Troubleshooting

**Server won't start:**
- Check if port 5555 is already in use
- Try changing the port in `server/server.py`

**Can't connect:**
- Make sure server is running first
- Check firewall settings

**Import errors:**
- Run: `pip install -r requirements.txt`

## Features to Try

✅ **Send Messages**: Just type and send!  
✅ **Reply**: Right-click a message → Reply  
✅ **Edit**: Right-click your message → Edit  
✅ **Delete**: Right-click your message → Delete  
✅ **File Sharing**: Click 📎 and select a file  
✅ **Multiple Rooms**: Join different rooms in different windows  
✅ **Typing Indicators**: Start typing to see it in action  
✅ **Online Users**: See who's online in the room  

Enjoy your WhatsApp-like chat! 🎉