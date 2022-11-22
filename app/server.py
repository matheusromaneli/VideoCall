from socket import socket
import socket
from util.user import User
from util.thread import thread
from util.message import Message
from util.wsocket import WSocket
from util.connection_table import ConnectionTable

class Server:
    def __init__(self, ip='localhost', port=5000) -> None:
        self.socket = WSocket(socket.create_server((ip,port)))
        self.connections = ConnectionTable()

        thread(self.wait_connections,())

    def wait_connections(self):
        self.socket.listen()
        while True:
            conn, _ = self.socket.accept()
            thread(self.client_thread, (WSocket(conn), ))

    def client_thread(self, connection: WSocket):
        try:
            current_user = None
            state = "waiting_register"
            message = None
            while True:
                if message == None:
                    message = connection.recv(1024)

                elif state == "waiting_register" and message.type == Message.kind("register"):
                    user = self.connections.find_by("name", message.user_name)

                    if user == None:
                        current_user = User(connection, message.user_name, message.ip, message.porta)
                        self.connections.append(current_user)
                        self.send(Message("accepted_register"), current_user)
                        self.update_users_list()
                        state = "idle"
                        message = None

                    else:
                        #NOTE Send connection since current_user doesnt exist yet
                        self.send(Message("declined_register"), connection) 
                        message = None

                elif state == "idle":
                    if message.type == Message.kind("registry"):
                        user = self.connections.find_by("name", message.user_name)
                        if user == None:
                            self.send(Message("not_found"), current_user)

                        else:
                            self.send(Message("registry", user = user.jsonfy()), current_user)
                        message = None

                    elif message.type == Message.kind("unregister"):
                        self.send(Message("accepted_unregister"), current_user)
                        self.connections.remove(current_user)
                        self.update_users_list()
                        connection.close()
                        return

                else:
                    if current_user:
                        self.send(Message("unexpected_message"), current_user)
                    else:
                        self.send(Message("unexpected_message"), connection)
                    message = None

        except Exception as e:
            if current_user:
                self.connections.remove(current_user)
            print(e)
            return

    def send(self, message: Message, user: User):
        user.send(message)

    def update_users_list(self):
        for connection in self.connections.active_connections:
            user = self.connections.find_by("name", connection.name)
            self.send(Message("users_list", data = self.connections.jsonfy()), user)