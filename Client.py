from Util import *
from Server import thread
import socket
from socket import socket as Socket

class Client:
    def __init__(self, ip='localhost', port=5000):
        self.name = None
        self.tcp = WSocket(Socket(family=socket.AF_INET, type=socket.SOCK_STREAM))
        self.last_registry = None

        self.udp = Socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.connected_to_udp = None

        self.udp.bind(("localhost",0))
        self.tcp.connect((ip,port))

        self.tcp_state = "unregistered"
        self.udp_state = "idle"

        thread(self.tcp_listen, ())
        thread(self.udp_listen, ())

    @property
    def udp_address(self):
        return self.udp.getsockname()

    def send(self, msg: Message):
        if msg.t == Message.kind("register") and self.tcp_state == "unregistered":
            self.name = msg.user_name
            self.tcp_state = "waiting_register"

        if msg.t == Message.kind("registry") and self.tcp_state == "idle":
            self.tcp_state = "waiting_registry"

        if msg.t == Message.kind("unregister") and self.tcp_state == "idle":
            self.tcp_state = "disconnecting"

        self.tcp.send(msg)

    def udp_send(self, msg: Message, address):
        if msg.t == Message.kind("call_request") and self.udp_state == "idle":
            self.udp_state = "waiting_response"

        if msg.t == Message.kind("end_call") and self.udp_state == "on_call":
            self.udp_state = "idle"
            self.connected_to_udp = None

        self.udp.sendto(msg.encode(), address)

    def tcp_listen(self):
        msg = None
        while 1:
            msg = self.tcp.recv(1024)

            # elif self.tcp_state == "unregistered":
            #     pass

            if self.tcp_state == "waiting_register" and msg.t == Message.kind("accepted_register"):
                print("Succesfully registered!")
                self.tcp_state = "idle"
                

            elif self.tcp_state == "waiting_register" and msg.t == Message.kind("declined_register"):
                print("Some user with that name already exists! Choose another one.")
                self.name = None
                self.tcp_state = "unregistered"
                


            # elif self.tcp_state == "idle":
            #     pass

            elif self.tcp_state == "waiting_registry" and msg.t == Message.kind("registry"):
                self.last_registry = msg.user
                print(json.dumps(msg.user))
                self.tcp_state = "idle"
                
        
            elif self.tcp_state == "disconnecting" and msg.t == Message.kind("accepted_unregister"):
                self.tcp.close()
                print("Disconnected!")
                return

    def call(self, ip, porta):
        self.udp_send(Message("call_request", user_name= self.name),(ip,porta))
    def end_call(self):
        self.udp_send(Message("end_call"),self.connected_to_udp)

    def send_voice(self, voice: bytes):
        self.sendto(Message("voice", voice=voice).encode(), self.connected_to_udp)
    def received_voice(self, voice: bytes):
        ## Tocar o audio usando pyaudio
        pass

    def udp_listen(self):
        msg = None
        while 1:
            data, address = self.udp.recvfrom(1024)
            msg = Message.decode(data)

            if self.udp_state == "idle" and msg.t == Message.kind("call_request"):
                r = input(f"User {msg.user_name} is calling! Type 1 to answer and 0 to reject it: ")
                r = int(r)
                if r == 1:
                    self.udp_send(Message("accept_call"), address)
                    self.connected_to_udp = address
                    self.udp_state = "on_call"
                else:
                    self.udp_send(Message("reject_call"), address)

            elif self.udp_state == "on_call" and msg.t == Message.kind("call_request"):
                self.udp_send(Message("occupied"), address)


            elif self.udp_state == "waiting_response" and msg.t == Message.kind("accept_call"):
                self.connected_to_udp = address
                self.udp_state = "on_call"
                
            elif self.udp_state == "waiting_response" and msg.t == Message.kind("reject_call"):
                self.udp_state = "idle"
        

            elif self.udp_state == "on_call" and msg.t == Message.kind("voice") and address == self.connected_to_udp:
                self.received_voice(msg.voice)
            elif self.udp_state == "on_call" and msg.t == Message.kind("end_call"):
                self.connected_to_udp = None
                self.udp_state = "idle"