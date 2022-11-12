from Util import *
from Server import thread
import socket
from socket import socket as Socket

class Client:
    def __init__(self, ip='localhost', port=5000):
        self.s = WSocket(Socket(family=socket.AF_INET, type=socket.SOCK_STREAM))
        self.s.connect((ip,port))
        self.state = "unregistered"

        thread(self.listen_to_server, ())

    def send(self, msg: Message):
        if msg.t == Message.kind("register") and self.state == "unregistered":
            self.state = "waiting_register"

        if msg.t == Message.kind("registry") and self.state == "idle":
            self.state = "waiting_registry"

        if msg.t == Message.kind("unregister") and self.state == "idle":
            self.state = "disconnecting"

        self.s.send(msg)

    def listen_to_server(self):
        msg = None
        while 1:
            if msg == None:
                msg = self.s.recv(1024)

            # elif self.state == "unregistered":
            #     msg = None

            elif self.state == "waiting_register" and msg.t == Message.kind("accepted_register"):
                print("Succesfully registered!")
                self.state = "idle"
                msg = None

            elif self.state == "waiting_register" and msg.t == Message.kind("declined_register"):
                print("Some user with that name already exists! Choose another one.")
                self.state = "unregistered"
                msg = None


            # elif self.state == "idle":
            #     pass

            elif self.state == "waiting_registry" and msg.t == Message.kind("registry"):
                print(json.dumps(msg.user))
                self.state = "idle"
                msg = None
        
            elif self.state == "disconnecting" and msg.t == Message.kind("accepted_unregister"):
                self.s.close()
                print("Disconnected!")
                return

            else:
                msg = None



# def udp_listen():
#     msg = None
#         while 1:
#             if msg == None:
#                 msg = self.s.recv(1024)

#             if self.state == "idle":
#                 if msg.t == Message.kind("call_request"):
#                     r = input(f"User {msg.user_name} is calling! Type 1 to answer and 0 to reject it: ")
#                     if r == 1:
#                         # send accept
#                         # self.state = "on_call"
#                         pass
#                     else:
#                         pass

#             if self.state == "waiting_response":
#                 pass
        
#             if self.state == "on_call":
#                 pass