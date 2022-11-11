from socket import socket as Socket
import socket
from threading import Thread
from Util import *

def thread(fn, args):
    t = Thread(target=fn, args=args, daemon=True)
    t.start()


class User:
    def __init__(self, socket: WSocket, name: str, udp_address: str):
        self.name = name
        self.udp_address = udp_address
        self.socket = socket

    def send(self, msg: Message):
        self.socket.send(msg)

    def recv(self, *args, **kwargs):
        return self.socket.recv(*args, **kwargs)

    def jsonfy(self):
        return {'name':self.name, 'udp':self.udp_address}

class Users():
    def __init__(self, users = []):
        self.users = users

    def get(self, name: str):
        for user in self.users:
            if user.name == name:
                return user
    def get_by(self, key, value):
        for user in self.users:
            if user.__getattribute__(key) == value:
                return user

    def __iter__(self):
        return iter(self.users)

    def append(self, user: User):
        self.users.append(user)
    def remove(self, user: User):
        self.users.remove(user)

    def jsonfy(self):
        return {"users": [x.jsonfy() for x in self.users]}


class Server:
    def __init__(self, ip='localhost', port=11111) -> None:
        self.s = socket.create_server((ip,port))
        self.s = WSocket(self.s)

        self.states = []
        self.users = Users
        thread(self.wait_connections,())

    def wait_connections(self):
        self.s.listen()
        while (1):
            conn, addr = self.s.accept()
            thread(self.client_thread, (WSocket(conn),))

    def client_thread(self, conn: WSocket):
        try:
            state = "waiting_register"
            msg = None
            while 1:
                if msg == None:
                    msg = conn.recv(1024)

                elif state == "waiting_register" and msg.t == Message.kind("register"):
                    user = Users.get(msg.user_name)
                    if user == None:
                        user = User(conn, msg.user_name, msg.udp_address)
                        self.users.append(user)
                        self.send(Message("accepted_register"))
                        state == "idle"
                        msg = None
                    else:
                        self.send(Message("declined_register"))
                        state == "waiting_register"
                        msg = None

                elif state == "idle" and msg.t == Message.kind("registry"):
                    # send back user or not_found
                    # set state to idle
                    msg = None
                    

                elif state == "idle" and msg.t == Message.kind("unregister"):
                    # remove user form list
                    # send confirmation
                    # close conn
                    # return
                    conn.close()
                    return

                else:
                    # send unexpected message
                    msg = None
                    
        except Exception as e:
            print(e)
            return


    def send(self, message: Message, names):
        for user in self.users:
            if user.name in names:
                user.send(message)