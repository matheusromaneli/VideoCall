from socket import socket as Socket
import socket
from threading import Thread
from Util import *

def table_print(cols,rows):
    spaces = [len(x) + 2 for x in cols]
    for row in rows:
        i = 0
        for col in row:
            if len(col) + 2 > spaces[i]:
                spaces[i] = len(col) + 2
            i+=1

    print(spaces)

    for x in range(len(cols)):
        s = spaces[x] - len(cols[x])
        s2 = s%2
        s //= 2

        cols[x] = " "*s + cols[x] + " "*(s + s2)
    print("|" + "|".join(cols) + "|")

    for row in rows:
        x = 0
        for col in row:
            print("|",end="")
            s = spaces[x] - len(col)
            s2 = s%2
            s //= 2
            print(" "*s + col + " "*(s + s2),end="")

            x+=1
        print("|")
        
 

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

    def get(self, name: User):
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
        table_print(["Name", "UDP Address"], self.listfy())
    def remove(self, user: User):
        self.users.remove(user)

    def jsonfy(self):
        return {"users": [x.jsonfy() for x in self.users]}
    def listfy(self):
        return [[x.name, x.udp_address] for x in self.users]


class Server:
    def __init__(self, ip='localhost', port=5000) -> None:
        self.s = socket.create_server((ip,port))
        self.s = WSocket(self.s)

        self.users = Users()
        thread(self.wait_connections,())

    def wait_connections(self):
        self.s.listen()
        while (1):
            conn, addr = self.s.accept()
            thread(self.client_thread, (WSocket(conn),))

    def client_thread(self, conn: WSocket):
        try:
            this_user = None
            state = "waiting_register"
            msg = None
            while 1:
                if msg == None:
                    msg = conn.recv(1024)
                

                elif state == "waiting_register" and msg.t == Message.kind("register"):
                    a_user = self.users.get(msg.user_name)
                    if a_user == None:
                        this_user = User(conn, msg.user_name, msg.udp_address)
                        self.users.append(this_user)
                        self.send(Message("accepted_register"), this_user)
                        state = "idle"
                        msg = None
                    else:
                        self.send(Message("declined_register"), conn) ## Uses conn since this_user doesnt exist yet
                        state = "waiting_register"
                        msg = None

                elif state == "idle" and msg.t == Message.kind("registry"):
                    a_user = self.users.get(msg.user_name)
                    if a_user == None:
                        self.send(Message("not_found"), this_user)
                    else:
                        self.send(Message("registry",user=a_user.jsonfy()), this_user)
                    msg = None
                    

                elif state == "idle" and msg.t == Message.kind("unregister"):
                    self.send(Message("accepted_unregister"),this_user)
                    self.users.remove(this_user)
                    conn.close()
                    return

                else:
                    if this_user:
                        self.send(Message("unexpected_message"),this_user)
                    else:
                        self.send(Message("unexpected_message"),conn)
                    msg = None
                    
        except Exception as e:
            print(e)
            return


    def msend(self, message: Message, users):
        for user in users:
            self.send(message, user)
    def send(self, message: Message, user: User):
        user.send(message)