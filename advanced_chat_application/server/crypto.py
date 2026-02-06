# server/crypto.py
from cryptography.fernet import Fernet
import base64
import hashlib

# Room-based encryption keys (in production, store these securely)
ROOM_KEYS = {}


def generate_room_key(room_name):
    """Generate a deterministic key for a room based on room name"""
    # In production, use a proper key derivation function with salt
    # This is a simplified version for demonstration
    key_material = hashlib.sha256(room_name.encode()).digest()
    return base64.urlsafe_b64encode(key_material)


def get_room_cipher(room):
    """Get or create Fernet cipher for a room"""
    if room not in ROOM_KEYS:
        ROOM_KEYS[room] = generate_room_key(room)
    return Fernet(ROOM_KEYS[room])


def encrypt_message(room, message):
    """Encrypt a message for a specific room"""
    try:
        cipher = get_room_cipher(room)
        return cipher.encrypt(message.encode()).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return message  # Fallback to plaintext


def decrypt_message(room, encrypted_message):
    """Decrypt a message from a specific room"""
    try:
        cipher = get_room_cipher(room)
        return cipher.decrypt(encrypted_message.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return encrypted_message  # Fallback to returning as-is


def encrypt_file(room, file_data):
    """Encrypt file data for a specific room"""
    try:
        cipher = get_room_cipher(room)
        return cipher.encrypt(file_data)
    except Exception as e:
        print(f"File encryption error: {e}")
        return file_data


def decrypt_file(room, encrypted_data):
    """Decrypt file data from a specific room"""
    try:
        cipher = get_room_cipher(room)
        return cipher.decrypt(encrypted_data)
    except Exception as e:
        print(f"File decryption error: {e}")
        return encrypted_data