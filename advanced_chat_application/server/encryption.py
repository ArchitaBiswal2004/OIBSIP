from cryptography.fernet import Fernet

KEY = Fernet.generate_key()
cipher = Fernet(KEY)

def encrypt_message(msg: str) -> str:
    return cipher.encrypt(msg.encode()).decode()

def decrypt_message(token: str) -> str:
    return cipher.decrypt(token.encode()).decode()
