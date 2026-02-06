# client/socket_client.py
import socket
import json
import threading


class ChatClient:
    """Enhanced chat client with buffered I/O and session management"""

    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
        self.sock = None
        self.buffer = ""
        self.session = None
        self.username = None
        self.connected = False
        self.lock = threading.Lock()

    def connect(self):
        """Establish *** to server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def send(self, data):
        """Send JSON data to server"""
        if not self.connected:
            raise ConnectionError("Not connected to server")

        try:
            with self.lock:
                # Add session to all requests if available
                if self.session and "session" not in data:
                    data["session"] = self.session

                payload = json.dumps(data) + "\n"
                self.sock.sendall(payload.encode())
                return True
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False
            raise ConnectionError("Server disconnected")

    def recv(self):
        """Receive and parse JSON data from server"""
        try:
            while "\n" not in self.buffer:
                chunk = self.sock.recv(4096).decode()
                if not chunk:
                    self.connected = False
                    return None
                self.buffer += chunk

            line, self.buffer = self.buffer.split("\n", 1)
            return json.loads(line.strip())

        except Exception as e:
            print(f"Receive error: {e}")
            self.connected = False
            return None

    def authenticate(self, username, password, action="login"):
        """
        Authenticate with server
        action: 'login' or 'register'
        Returns: (success, message)
        """
        if not self.connected:
            if not self.connect():
                return False, "Cannot connect to server"

        self.send({
            "action": action,
            "username": username,
            "password": password
        })

        response = self.recv()
        if not response:
            return False, "No response from server"

        if response.get("ok"):
            self.session = response.get("session")
            self.username = username
            return True, response.get("msg", "Success")
        else:
            return False, response.get("msg", "Authentication failed")

    def join_room(self, room):
        """Join a chat room"""
        self.send({
            "type": "join",
            "room": room,
            "session": self.session
        })

        # Wait for confirmation
        response = self.recv()
        return response.get("ok", False)

    def send_message(self, message, message_id, reply_to=None):
        """Send a chat message"""
        self.send({
            "type": "chat",
            "message": message,
            "message_id": message_id,
            "reply_to": reply_to,
            "session": self.session
        })

    def send_typing_indicator(self, is_typing=True):
        """Send typing indicator"""
        self.send({
            "type": "typing",
            "typing": is_typing,
            "session": self.session
        })

    def mark_as_read(self, message_id):
        """Mark a message as read"""
        self.send({
            "type": "read",
            "message_id": message_id,
            "session": self.session
        })

    def edit_message(self, message_id, new_text):
        """Edit a message"""
        self.send({
            "type": "edit",
            "message_id": message_id,
            "message": new_text,
            "session": self.session
        })

    def delete_message(self, message_id):
        """Delete a message"""
        self.send({
            "type": "delete",
            "message_id": message_id,
            "session": self.session
        })

    def upload_file(self, message_id, filename, file_type, file_data_b64):
        """Upload a file attachment"""
        self.send({
            "type": "upload",
            "message_id": message_id,
            "filename": filename,
            "file_type": file_type,
            "file_data": file_data_b64,
            "session": self.session
        })

    def download_file(self, message_id):
        """Download a file attachment"""
        self.send({
            "type": "download",
            "message_id": message_id,
            "session": self.session
        })

        return self.recv()

    def close(self):
        """Close ***"""
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass

    def is_connected(self):
        """Check if client is connected"""
        return self.connected