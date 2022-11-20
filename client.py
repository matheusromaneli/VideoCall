import base64
from util.message import Message
from util.thread import thread
from util.wsocket import WSocket
import socket
from socket import socket as Socket
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
class Client:
    def __init__(
            self,
            on_tcp_state_change = lambda : None,
            on_udp_state_change = lambda : None
        ):
        
        self.name = None
        self.tcp = None
        self.last_registry = None

        self.udp = Socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.connected_to_udp = None
        self.connected_to_udp_username = "?"

        self.udp.bind(("localhost", 0))

        self._tcp_state = "offline"
        self.on_tcp_state_change = on_tcp_state_change

        self._udp_state = "idle"
        self.on_udp_state_change = on_udp_state_change

        self.on_voice_receive = lambda x : None

        thread(self.udp_listen, ())


    def connect_to_server(self, ip, port=5000):
        try:
            self.tcp = WSocket(Socket(family=socket.AF_INET, type=socket.SOCK_STREAM))
            self.tcp.connect((ip, port))
            thread(self.tcp_listen, ())
        except Exception as e:
            print("Failed to connect to server with error:\n", e)

    #### Make pyqt5 easier to handle
    @property
    def tcp_state(self):
        return self._tcp_state
    @tcp_state.setter
    def tcp_state(self, _v):
        self._tcp_state = _v
        self.on_tcp_state_change()

    @property
    def udp_state(self):
        return self._udp_state
    @udp_state.setter
    def udp_state(self, _v):
        self._udp_state = _v
        self.on_udp_state_change()
    ################################

    #### Is a function since you can get it off of the socket
    @property
    def udp_address(self):
        return self.udp.getsockname()
    ###################

    def send(self, msg: Message):
        if msg.type == Message.kind("register") and self.tcp_state == "unregistered":
            self.name = msg.user_name
            self.tcp_state = "waiting_register"

        if msg.type == Message.kind("registry") and self.tcp_state == "idle":
            self.tcp_state = "waiting_registry"

        if msg.type == Message.kind("unregister") and self.tcp_state == "idle":
            self.tcp_state = "disconnecting"

        self.tcp.send(msg)

    def udp_send(self, msg: Message, address):
        if self.udp_state == "idle" and msg.type == Message.kind("call_request"):
            self.udp_state = "waiting_response"
        
        elif self.udp_state == "received_request":
            if msg.type == Message.kind("accept_call"):
                self.udp_state = "on_call"

            elif msg.type == Message.kind("reject_call"):
                self.udp_state = "idle"

        elif self.udp_state in ["on_call", "waiting_response"] and msg.type == Message.kind("end_call"):
            self.udp_state = "idle"
            self.connected_to_udp = None
            self.connected_to_udp_username = "?"

        if address == None: return
        self.udp.sendto(msg.encode(), address)

    def tcp_listen(self):
        try:
            self.tcp_state = "unregistered"
            message = None
            while True:
                message = self.tcp.recv(1024)

                if self.tcp_state == "waiting_register":
                    if message.type == Message.kind("accepted_register"):
                        print("Succesfully registered!")
                        self.tcp_state = "idle"

                    elif message.type == Message.kind("declined_register"):
                        print("Some user with that name already exists! Choose another one.")
                        self.name = None
                        self.tcp_state = "unregistered"

                elif self.tcp_state == "waiting_registry":
                    if message.type == Message.kind("registry"):
                        self.last_registry = message.user
                        self.tcp_state = "idle"

                    elif message.type == Message.kind("not_found"):
                        self.last_registry = False
                        self.tcp_state = "idle"

                elif self.tcp_state == "disconnecting" and message.type == Message.kind("accepted_unregister"):
                    self.tcp.close()
                    self.tcp_state = "offline"
                    return

        except Exception as e:
            print(e)
            self.tcp_state = "offline"

    def udp_listen(self):
        msg = None
        while 1:
            data, address = self.udp.recvfrom(4096)
            msg = Message.decode(data)
            if self.udp_state == "idle" and msg.type == Message.kind("call_request"):
                self.connected_to_udp = address
                self.connected_to_udp_username = msg.user_name
                self.udp_state = "received_request"

            elif self.udp_state != "idle" and msg.type == Message.kind("call_request"):
                self.udp_send(Message("occupied"), address)


            elif self.udp_state == "waiting_response":
                if msg.type == Message.kind("accept_call"):
                    self.connected_to_udp = address
                    self.connected_to_udp_username = msg.name
                    self.udp_state = "on_call"
                
                elif  msg.type in [Message.kind("reject_call"), Message.kind("occupied")]:
                    self.udp_state = "idle"
        

            elif self.udp_state == "on_call": 
                if msg.type == Message.kind("voice") and address == self.connected_to_udp:
                    self.received_voice(base64.b64decode(msg.voice))
                
                elif msg.type == Message.kind("end_call"):
                    self.connected_to_udp = None
                    self.connected_to_udp_username = None
                    self.udp_state = "idle"


    def login(self, username):
        self.send(
            Message(
                "register",
                user_name = username, 
                ip = self.udp_address[0], 
                porta = self.udp_address[1]
            )
        )

    def logoff(self):
        self.send(Message("unregister"))

    def call_user(self, user_name):
        self.last_registry = None
        self.send(Message("registry", user_name=user_name))

        while self.last_registry == None: ## Will be false if user doesnt exist
            pass
        if self.last_registry == False:
            return

        user_to_call = self.last_registry
        self.call(user_to_call['ip'], user_to_call['porta'])

    def respond_call_request(self, accept=True):
        if accept:
            self.udp_send(
                Message("accept_call", user_name = self.name),
                self.connected_to_udp
            )
        else:
            self.udp_send(
                Message("reject_call",  user_name = self.name),
                self.connected_to_udp
            )

    def call(self, ip, porta):
        self.udp_send(Message("call_request", user_name= self.name),(ip,porta))

    def end_call(self):
        self.udp_send(Message("end_call"), self.connected_to_udp)

    def send_voice(self, voice: bytes):
        if self.connected_to_udp:
            self.udp_send(
                Message("voice", voice=base64.b64encode(voice).decode('ascii')),
                self.connected_to_udp
            )

    def received_voice(self, voice: bytes):
        self.on_voice_receive(voice)
