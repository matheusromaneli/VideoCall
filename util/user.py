from util.message import Message
from util.wsocket import WSocket


class User:
    def __init__(self, socket: WSocket, name: str, ip: str, porta: int):
        self.name = name
        self.ip = ip
        self.porta = porta
        self.socket = socket

    def send(self, msg: Message):
        self.socket.send(msg)

    def recv(self, *args, **kwargs):
        return self.socket.recv(*args, **kwargs)

    def jsonfy(self):
        return {"name": self.name, "ip": self.ip, "porta": self.porta}
