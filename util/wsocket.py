from util.message import Message


class WSocket:
    def __init__(self, socket) -> None:
        self.socket = socket
        self.buffered_message = []

    def accept(self, *args, **kwargs):
        resp = self.socket.accept(*args, **kwargs)
        print("$$ connection accepted!")
        return resp

    def sendto(self, *args, **kwargs):
        return self.socket.sendto(*args, **kwargs)

    def recvfrom(self, *args, **kwargs):
        resp = self.socket.recvfrom(*args, **kwargs)
        return resp

    def send(self, msg: Message, *args, **kwargs):
        print(">>", msg.__repr__())
        self.socket.send(msg.encode() + b"\0", *args, **kwargs)

    def recv(self, *args, **kwargs) -> Message:
        if self.buffered_message == []:
            data = self.socket.recv(*args, **kwargs)
            self.buffered_message += data.split(b"\0")[:-1]

        ## Try to decode. If it fails, message is broken, so ignore it.
        msg = self.buffered_message.pop(0)
        try:
            msg = Message.decode(msg)
            print("<<", msg.__repr__())

        except:
            return self.recv(*args, **kwargs)  ## Ignore and try again

        return msg  ## Decoded correctly

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except:
            return self.socket.__getattribute__(__name)
