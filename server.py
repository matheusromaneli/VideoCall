from socket import socket
import socket
from util.message import Message
from util.user import User
from util.wsocket import WSocket
from util.thread import thread

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

    # def find_by(self, name: User):
    #     for user in self.users:
    #         if user.name == name:
    #             return user

    def find_by(self, key, value):
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
            current_user = None
            state = "waiting_register"
            message = None
            while 1:
                if message == None:
                    message = connection.recv(1024)

                elif state == "waiting_register" and message.type == Message.kind("register"):
                    user = self.users.find_by("name", message.user_name)

                    if user == None:
                        current_user = User(connection, message.user_name, message.ip, message.porta)
                        self.users.append(current_user)
                        self.send(Message("accepted_register"), current_user)
                        state = "idle"
                        message = None

                    else:
                        #NOTE Send connection since current_user doesnt exist yet
                        self.send(Message("declined_register"), connection) 
                        message = None

                elif state == "idle":
                    if message.type == Message.kind("registry"):
                        user = self.users.find_by("name", message.user_name)
                        if user == None:
                            self.send(Message("not_found"), current_user)
                        else:
                            self.send(Message("registry", user = user.jsonfy()), current_user)
                        message = None

                    elif message.type == Message.kind("unregister"):
                        self.send(Message("accepted_unregister"), current_user)
                        self.users.remove(current_user)
                        connection.close()
                        return
                
                    elif message.type == Message.kind("name_list"):
                        self.send(Message("name_list"), )
                        message = None

                else:
                    if current_user:
                        self.send(Message("unexpected_message"), current_user)
                    else:
                        self.send(Message("unexpected_message"), connection)
                    message = None
                    
        except Exception as e:
            if current_user:
                self.users.remove(current_user)
            print(e)
            return

    # def msend(self, message: Message, users):
    #     for user in users:
    #         self.send(message, user)

    def send(self, message: Message, user: User):
        user.send(message)