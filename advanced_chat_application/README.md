# Advanced Chat Application

A production-ready, feature-rich chat application built with Python and Tkinter, inspired by WhatsApp.

## Features ✨

### Core Features
- **User Authentication**: Secure registration and login with bcrypt password hashing
- **Real-time Messaging**: Instant message delivery using socket programming
- **Multiple Chat Rooms**: Create or join different chat rooms
- **End-to-End Encryption**: Messages encrypted using Fernet symmetric encryption
- **Message Persistence**: All messages stored in SQLite database

### Advanced Features
- **Typing Indicators**: See when others are typing
- **Read Receipts**: Track who has read your messages
- **Message Editing**: Edit sent messages (with edited indicator)
- **Message Deletion**: Delete your own messages
- **Reply to Messages**: Quote and reply to specific messages
- **File Attachments**: Send images and documents (up to 5MB)
- **User Presence**: See who's online in each room
- **Message History**: Load previous messages when joining a room
- **Session Management**: Secure session tokens with expiration
- **Modern UI**: WhatsApp-inspired interface with message bubbles

## Installation 🚀

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage 📱

### Starting the Server

Run the server first:
```bash
python run_server.py
```

The server will start on `127.0.0.1:5555` by default.

### Starting the Client

In a new terminal, run the client:
```bash
python main.py
```

### Using the Application

1. **Register/Login**: Create a new account or login with existing credentials
2. **Select Room**: Choose a chat room or create a new one
3. **Start Chatting**: Send messages, files, and interact with other users!

### Running Multiple Clients

To test the chat, open multiple terminals and run `python main.py` in each to simulate different users.

## Project Structure 📁

```
advanced_chat_application/
├── server/
│   ├── server.py          # Main server logic
│   ├── auth.py            # Authentication handlers
│   ├── database.py        # Database operations
│   └── crypto.py          # Encryption utilities
├── client/
│   ├── socket_client.py   # Socket client wrapper
│   ├── login_ui.py        # Login/registration UI
│   ├── room_ui.py         # Room selection UI
│   └── chat_ui.py         # Main chat interface
├── main.py                # Client entry point
├── run_server.py          # Server entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Technical Details 🔧

### Architecture
- **Server**: Multi-threaded TCP socket server
- **Client**: Threaded Tkinter GUI with async message handling
- **Protocol**: JSON-based message protocol over TCP
- **Database**: SQLite for persistence
- **Encryption**: Fernet (AES-128 CBC with HMAC)

### Security Features
- Password hashing with bcrypt (cost factor 12)
- Session-based authentication with expiration
- Room-based message encryption
- SQL injection prevention using parameterized queries

### Database Schema
- **users**: User accounts and credentials
- **messages**: Chat messages with encryption
- **read_receipts**: Message read tracking
- **typing_status**: Real-time typing indicators
- **attachments**: File storage
- **sessions**: Authentication sessions

## Keyboard Shortcuts ⌨️

- **Enter**: Send message (in login/room selection)
- **Ctrl+Enter**: Send message (in chat)
- **Right-click**: Context menu (reply, edit, delete, copy)

## Configuration ⚙️

### Server Configuration
Edit `server/server.py`:
```python
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5555       # Server port
```

### Client Configuration
Edit `main.py`:
```python
LoginWindow(host="127.0.0.1", port=5555)
```

## Limitations ⚠️

- File size limit: 5MB
- No video/voice calls
- No group admin features
- No message search functionality
- Limited to local network (without port forwarding)

## Future Enhancements 🚀

- [ ] Group chat with admin controls
- [ ] User profiles with avatars
- [ ] Message search and filtering
- [ ] Emoji picker
- [ ] Dark mode
- [ ] Message reactions
- [ ] Voice messages
- [ ] Video/voice calls
- [ ] Status updates
- [ ] Push notifications

## Troubleshooting 🔍

### Connection Issues
- Ensure server is running before starting clients
- Check firewall settings
- Verify correct host and port

### Database Issues
- Delete `server/chat.db` to reset database
- Ensure write permissions in server directory

### Import Errors
- Install all dependencies: `pip install -r requirements.txt`
- Ensure Python 3.8+ is installed

## License 📄

This is an educational project. Feel free to use and modify as needed.

## Credits 👏

Built as an advanced chat application demonstration project.