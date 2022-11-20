from socket import socket
import socket
from util.message import Message
from util.user import User
from util.wsocket import WSocket
from util.thread import *

def table(cols,rows):
    rows = [[str(x) for x in col] for col in rows]
    out = ""

    spaces = [len(x) + 2 for x in cols]
    for row in rows:
        i = 0
        for col in row:
            if len(col) + 2 > spaces[i]:
                spaces[i] = len(col) + 2
            i+=1

    for x in range(len(cols)):
        s = spaces[x] - len(cols[x])
        s2 = s%2
        s //= 2

        cols[x] = " "*s + cols[x] + " "*(s + s2)
    out += "|" + "|".join(cols) + "|\n"

    for row in rows:
        x = 0
        for col in row:
            out += "|"
            s = spaces[x] - len(col)
            s2 = s%2
            s //= 2
            out += " "*s + col + " "*(s + s2)

            x+=1
        out += "|\n"
        
    return out

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
        print(table(["Name", "Ip", "Porta"], self.listfy()))
    def remove(self, user: User):
        self.users.remove(user)

    def jsonfy(self):
        return {"users": [x.jsonfy() for x in self.users]}
    def listfy(self):
        return [[x.name, x.ip, x.porta] for x in self.users]


class Server:
    def __init__(self, ip='localhost', port=5000) -> None:
        self.socket = WSocket(socket.create_server((ip,port)))
        self.users = Users()

        thread(self.wait_connections,())

    def wait_connections(self):
        self.socket.listen()
        while (1):
            connection, _ = self.socket.accept()
            thread(self.client_thread, (WSocket(connection)))

    def client_thread(self, connection: WSocket):
        try:
            this_user = None
            state = "waiting_register"
            message = None
            while 1:
                if message == None:
                    message = connection.recv(1024)

                elif state == "waiting_register" and message.t == Message.kind("register"):
                    a_user = self.users.get(message.user_name)
                    if a_user == None:
                        this_user = User(connection, message.user_name, message.ip, message.porta)
                        self.users.append(this_user)
                        self.send(Message("accepted_register"), this_user)
                        state = "idle"
                        message = None
                    else:
                        self.send(Message("declined_register"), connection) ## Uses connection since this_user doesnt exist yet
                        state = "waiting_register"
                        message = None

                elif state == "idle" and message.t == Message.kind("registry"):
                    a_user = self.users.get(message.user_name)
                    if a_user == None:
                        self.send(Message("not_found"), this_user)
                    else:
                        self.send(Message("registry",user=a_user.jsonfy()), this_user)
                    message = None
                    

                elif state == "idle" and message.t == Message.kind("unregister"):
                    self.send(Message("accepted_unregister"),this_user)
                    self.users.remove(this_user)
                    connection.close()
                    return

                else:
                    if this_user:
                        self.send(Message("unexpected_message"),this_user)
                    else:
                        self.send(Message("unexpected_message"),connection)
                    message = None
                    
        except Exception as e:
            if this_user:
                self.users.remove(this_user)
            print(e)
            return


    def msend(self, message: Message, users):
        for user in users:
            self.send(message, user)

    def send(self, message: Message, user: User):
        user.send(message)