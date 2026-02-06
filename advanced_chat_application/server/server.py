# server/server.py
import socket
import threading
import json
import base64
from datetime import datetime
from collections import defaultdict
import traceback
from server.auth import register_user, login_user, authenticate_session
from server.database import (
    init_db, save_message, fetch_room_history, delete_message,
    edit_message, clear_room, mark_message_read, get_read_receipts,
    update_typing_status, get_typing_users, save_attachment, get_attachment
)
from server.crypto import encrypt_message, decrypt_message, encrypt_file, decrypt_file

HOST, PORT = "0.0.0.0", 5555

# Connected clients: {socket: {username, room, session}}
clients = {}
clients_lock = threading.Lock()

# Room memberships: {room: set(usernames)}
rooms = defaultdict(set)
rooms_lock = threading.Lock()


class ClientConnection:
    """Wrapper for client socket with buffered reading"""

    def __init__(self, sock):
        self.sock = sock
        self.buffer = ""

    def send(self, data):
        """Send JSON data to client"""
        try:
            payload = json.dumps(data) + "\n"
            self.sock.sendall(payload.encode())
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False

    def recv(self):
        """Receive and parse JSON data from client"""
        try:
            while "\n" not in self.buffer:
                chunk = self.sock.recv(4096).decode()
                if not chunk:
                    print(f"[DEBUG] Socket closed, no data received")
                    return None
                self.buffer += chunk

            line, self.buffer = self.buffer.split("\n", 1)
            parsed = json.loads(line.strip())
            print(f"[DEBUG] Received: {parsed}")
            return parsed
        except json.JSONDecodeError as e:
            print(f"[!] JSON decode error: {e}, data: {line if 'line' in locals() else 'N/A'}")
            return None
        except Exception as e:
            print(f"[!] Receive error: {e}")
            traceback.print_exc()
            return None

    def close(self):
        """Close socket ***"""
        try:
            self.sock.close()
        except:
            pass


def broadcast_to_room(room, data, exclude_sock=None):
    """Broadcast message to all clients in a room"""
    with clients_lock:
        for sock, info in list(clients.items()):
            if info.get("room") == room and sock != exclude_sock:
                ClientConnection(sock).send(data)


def get_room_users(room):
    """Get list of usernames in a room"""
    with clients_lock:
        return [
            info["username"]
            for sock, info in clients.items()
            if info.get("room") == room
        ]


def handle_authentication(conn, data):
    """Handle login/register requests"""
    action = data.get("action")
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if action == "register":
        ok, msg, session = register_user(username, password)
    elif action == "login":
        ok, msg, session = login_user(username, password)
    else:
        conn.send({"ok": False, "msg": "Invalid action"})
        return None, None

    conn.send({
        "ok": ok,
        "msg": msg,
        "session": session,
        "username": username if ok else None
    })

    return (username, session) if ok else (None, None)


def handle_join_room(conn, sock, data):
    """Handle user joining a chat room"""
    room = data.get("room", "").strip()
    session = data.get("session")

    username = authenticate_session(session)
    if not username:
        conn.send({"ok": False, "msg": "Invalid session"})
        return

    # Update client info
    with clients_lock:
        clients[sock]["room"] = room
        clients[sock]["username"] = username

    with rooms_lock:
        rooms[room].add(username)

    # Send room history
    history = fetch_room_history(room, limit=50)
    for row in history:
        sender = row["sender"]
        encrypted_msg = row["message"]
        msg_id = row["message_id"]
        timestamp = row["time"]
        reply_to = row["reply_to"]
        edited = row["edited_at"]

        # Decrypt message
        plain_msg = decrypt_message(room, encrypted_msg)

        conn.send({
            "type": "chat",
            "sender": sender,
            "message": plain_msg,
            "message_id": msg_id,
            "timestamp": timestamp,
            "reply_to": reply_to,
            "edited": bool(edited)
        })

    # Notify room about new user
    broadcast_to_room(room, {
        "type": "user_joined",
        "username": username,
        "users": get_room_users(room)
    })

    conn.send({
        "ok": True,
        "room": room,
        "users": get_room_users(room)
    })


def handle_chat_message(conn, sock, data):
    """Handle incoming chat message"""
    session = data.get("session")
    username = authenticate_session(session)

    if not username:
        conn.send({"ok": False, "msg": "Authentication required"})
        return

    with clients_lock:
        room = clients.get(sock, {}).get("room")

    if not room:
        conn.send({"ok": False, "msg": "Not in a room"})
        return

    message = data.get("message", "").strip()
    message_id = data.get("message_id")
    reply_to = data.get("reply_to")

    if not message:
        return

    # Encrypt and save message
    encrypted_msg = encrypt_message(room, message)
    save_message(room, username, encrypted_msg, message_id, reply_to)

    # Broadcast to room (plaintext)
    timestamp = datetime.now().strftime("%H:%M")
    broadcast_to_room(room, {
        "type": "chat",
        "sender": username,
        "message": message,
        "message_id": message_id,
        "timestamp": timestamp,
        "reply_to": reply_to,
        "edited": False
    })


def handle_typing_indicator(conn, sock, data):
    """Handle typing indicator"""
    session = data.get("session")
    username = authenticate_session(session)

    if not username:
        return

    with clients_lock:
        room = clients.get(sock, {}).get("room")

    if not room:
        return

    is_typing = data.get("typing", False)

    if is_typing:
        update_typing_status(room, username)

    # Broadcast typing users to room
    typing_users = [u for u in get_typing_users(room) if u != username]

    broadcast_to_room(room, {
        "type": "typing",
        "users": typing_users
    }, exclude_sock=sock)


def handle_read_receipt(conn, sock, data):
    """Handle message read receipt"""
    session = data.get("session")
    username = authenticate_session(session)

    if not username:
        return

    message_id = data.get("message_id")
    if not message_id:
        return

    mark_message_read(message_id, username)

    with clients_lock:
        room = clients.get(sock, {}).get("room")

    if room:
        # Notify sender about read receipt
        receipts = get_read_receipts(message_id)
        broadcast_to_room(room, {
            "type": "read_receipt",
            "message_id": message_id,
            "readers": [r["username"] for r in receipts]
        })


def handle_edit_message(conn, sock, data):
    """Handle message edit request"""
    session = data.get("session")
    username = authenticate_session(session)

    if not username:
        return

    message_id = data.get("message_id")
    new_text = data.get("message", "").strip()

    with clients_lock:
        room = clients.get(sock, {}).get("room")

    if not room or not new_text:
        return

    # Encrypt and update
    encrypted_msg = encrypt_message(room, new_text)
    edit_message(message_id, encrypted_msg)

    # Broadcast edit
    broadcast_to_room(room, {
        "type": "message_edited",
        "message_id": message_id,
        "message": new_text,
        "edited_by": username
    })


def handle_delete_message(conn, sock, data):
    """Handle message deletion"""
    session = data.get("session")
    username = authenticate_session(session)

    if not username:
        return

    message_id = data.get("message_id")
    delete_message(message_id)

    with clients_lock:
        room = clients.get(sock, {}).get("room")

    if room:
        broadcast_to_room(room, {
            "type": "message_deleted",
            "message_id": message_id
        })


def handle_file_upload(conn, sock, data):
    """Handle file attachment upload"""
    session = data.get("session")
    username = authenticate_session(session)

    if not username:
        conn.send({"ok": False, "msg": "Authentication required"})
        return 

    message_id = data.get("message_id")
    filename = data.get("filename")
    file_type = data.get("file_type")
    file_data_b64 = data.get("file_data")

    if not all([message_id, filename, file_data_b64]):
        conn.send({"ok": False, "msg": "Missing file data"})
        return

    try:
        # Decode and encrypt file
        file_data = base64.b64decode(file_data_b64)

        with clients_lock:
            room = clients.get(sock, {}).get("room")

        encrypted_data = encrypt_file(room, file_data)
        save_attachment(message_id, filename, file_type, encrypted_data)

        conn.send({"ok": True, "message_id": message_id})

        # Notify room about file
        broadcast_to_room(room, {
            "type": "file_attached",
            "message_id": message_id,
            "filename": filename,
            "file_type": file_type,
            "sender": username
        })

    except Exception as e:
        conn.send({"ok": False, "msg": f"Upload failed: {e}"})


def handle_file_download(conn, sock, data):
    """Handle file download request"""
    session = data.get("session")
    username = authenticate_session(session)

    if not username:
        return

    message_id = data.get("message_id")
    attachment = get_attachment(message_id)

    if not attachment:
        conn.send({"ok": False, "msg": "File not found"})
        return

    with clients_lock:
        room = clients.get(sock, {}).get("room")

    # Decrypt and send file
    decrypted_data = decrypt_file(room, attachment["file_data"])
    file_b64 = base64.b64encode(decrypted_data).decode()

    conn.send({
        "ok": True,
        "filename": attachment["filename"],
        "file_type": attachment["file_type"],
        "file_data": file_b64
    })


def handle_client(sock, addr):
    """Main client handler with detailed error logging"""
    conn = ClientConnection(sock)
    username = None

    print(f"[+] New connection from {addr}")

    try:
        # Authentication phase
        print(f"[DEBUG] Waiting for auth data from {addr}...")
        auth_data = conn.recv()
        
        if not auth_data:
            print(f"[!] No auth data received from {addr}")
            return

        print(f"[DEBUG] Received auth data: {auth_data.get('action', 'NO ACTION')} from {addr}")
        
        username, session = handle_authentication(conn, auth_data)
        if not username:
            print(f"[!] Authentication failed for {addr}")
            return

        # Register client
        with clients_lock:
            clients[sock] = {
                "username": username,
                "session": session,
                "room": None,
                "addr": addr
            }

        print(f"[✓] {username} authenticated successfully")

        # Message handling loop
        while True:
            data = conn.recv()
            if not data:
                print(f"[DEBUG] No data received from {username}, closing connection")
                break

            msg_type = data.get("type")
            print(f"[DEBUG] Received message type '{msg_type}' from {username}")

            if msg_type == "join":
                handle_join_room(conn, sock, data)
            elif msg_type == "chat":
                handle_chat_message(conn, sock, data)
            elif msg_type == "typing":
                handle_typing_indicator(conn, sock, data)
            elif msg_type == "read":
                handle_read_receipt(conn, sock, data)
            elif msg_type == "edit":
                handle_edit_message(conn, sock, data)
            elif msg_type == "delete":
                handle_delete_message(conn, sock, data)
            elif msg_type == "upload":
                handle_file_upload(conn, sock, data)
            elif msg_type == "download":
                handle_file_download(conn, sock, data)
            else:
                print(f"[!] Unknown message type: {msg_type}")

    except json.JSONDecodeError as e:
        print(f"[!] JSON decode error from {username or addr}: {e}")
    except Exception as e:
        print(f"[!] Error handling {username or addr}: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        with clients_lock:
            client_info = clients.pop(sock, {})
            room = client_info.get("room")

        if room and username:
            with rooms_lock:
                rooms[room].discard(username)

            # Notify room about user leaving
            broadcast_to_room(room, {
                "type": "user_left",
                "username": username,
                "users": get_room_users(room)
            })

        conn.close()
        print(f"[-] {username or addr} disconnected")

def start_server():
    """Start the chat server"""
    init_db()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"✅ Server running on {HOST}:{PORT}")
    print("Waiting for ***s...")

    try:
        while True:
            client_sock, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(client_sock, addr),
                daemon=True
            ).start()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()