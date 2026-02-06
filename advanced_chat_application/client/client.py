import socket, json
from cryptography.fernet import Fernet

HOST="127.0.0.1"
PORT=5555

class ChatClient:
    def __init__(self, username, password, action):
        self.sock = socket.socket()
        self.sock.connect((HOST,PORT))
        self.username = username
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

        self.send({
            "action":action,
            "username":username,
            "password":password
        })
        if not self.recv()["ok"]:
            raise Exception("Auth failed")

    def send(self,d):
        self.sock.sendall((json.dumps(d)+"\n").encode())

    def recv(self):
        data=""
        while "\n" not in data:
            data+=self.sock.recv(4096).decode()
        return json.loads(data)
