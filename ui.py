import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from client import Client
import pyaudio
from util import *
from util.thread import thread

class CallPopUp(QDialog):
    def __init__(self, user_name="An unamed user", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Someone is calling you!")

        QBtn = QDialogButtonBox.Yes | QDialogButtonBox.No

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(f"{user_name} is calling you! Accept call?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class Window(QMainWindow):
    state_change = PyQt5.QtCore.pyqtSignal()
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(100,100,600,400)
        self.setWindowTitle("Voip!")
        self.console_history = []
        self.tcp_state = "offline"
        self.udp_state = "idle"

        self.state_change.connect(self.updated_state)
        self.client = Client(self.state_change.emit, self.state_change.emit)

        self.cw = QWidget()
        self.setCentralWidget(self.cw)
        flo = QFormLayout()

        ### Connection
        self.ip = QLineEdit()
        self.ip.setText("localhost")
        self.connect_btn = QPushButton('Connect to server', self)
        self.connect_btn.clicked.connect(self.connect)
        flo.addRow("Ip: (0.0.0.0)", self.ip)
        flo.addRow(self.connect_btn)
        ###################

        ### Login
        self.user_name = QLineEdit()
        self.user_name.setText("Bruno")
        self.login_btn = QPushButton('Login', self)
        self.login_btn.clicked.connect(self.login)
        flo.addRow("Login as:", self.user_name)
        flo.addRow(self.login_btn)
        ###################

        ### TCP server stuff
        self.server_status = QLabel(self)
        self.server_status.setGeometry(20,20,100,100)
        self.server_status.setText("[offline]")  
        flo.addRow("Server stauts: ", self.server_status)

        self.user_to_call = QLineEdit()
        flo.addRow("User name:", self.user_to_call)
        ###################

        ### Action bar
        hbox = QHBoxLayout()
        self.dc = QPushButton("Disconnect (from server)")
        self.dc.clicked.connect(self.disconnect)
        hbox.addWidget(self.dc)


        self.call_btn = QPushButton('Call user')
        self.call_btn.clicked.connect(self.call)
        hbox.addWidget(self.call_btn, 1)

        self.ec = QPushButton("End Call")
        self.ec.clicked.connect(self.end_call)
        hbox.addWidget(self.ec, 2)

        flo.addRow(hbox)
        ###################

        self.cw.setLayout(flo)

        self.updated_state()

    def updated_state(self):
        self.tcp_state = self.client.tcp_state
        self.udp_state = self.client.udp_state
        self.server_status.setText(f"[tcp:{self.tcp_state}, udp:{self.udp_state}]")

        ##### UDP ######
        if self.udp_state == "idle":
            self.ec.setDisabled(1)
            self.call_btn.setDisabled(0)
        if self.udp_state == "waiting_response":
            self.ec.setDisabled(0)
            self.call_btn.setDisabled(1)
        if self.udp_state == "received_request":
            self.client.respond_call_request(self.call_request_pop_up())
            self.ec.setDisabled(1)
            self.call_btn.setDisabled(1)
        if self.udp_state == "on_call":
            self.ec.setDisabled(0)
            self.call_btn.setDisabled(1)


        ###### TCP #######
        if self.tcp_state == "offline":
            ## Connect to server enabled
            self.ip.setDisabled(0)
            self.connect_btn.setDisabled(0)

            ## Set name disbled
            self.user_name.setDisabled(1)
            self.login_btn.setDisabled(1)

            ## Call disabled
            self.dc.setDisabled(1)
            self.call_btn.setDisabled(1)
            self.user_to_call.setDisabled(1)
            
        elif self.tcp_state == "unregistered":
            ## Connect to server enabled
            self.ip.setDisabled(1)
            self.connect_btn.setDisabled(1)

            ## Set name disbled
            self.user_name.setDisabled(0)
            self.login_btn.setDisabled(0)

            ## Call disabled
            self.dc.setDisabled(1)
            self.call_btn.setDisabled(1)
            self.user_to_call.setDisabled(1)
            
        elif self.tcp_state == "waiting_register":
            ## Connect to server enabled
            self.ip.setDisabled(1)
            self.connect_btn.setDisabled(1)

            ## Set name disbled
            self.user_name.setDisabled(1)
            self.login_btn.setDisabled(1)

            ## Call disabled
            self.dc.setDisabled(1)
            self.call_btn.setDisabled(1)
            self.user_to_call.setDisabled(1)
            
        elif self.tcp_state == "idle":
            ## Connect to server enabled
            self.ip.setDisabled(1)
            self.connect_btn.setDisabled(1)

            ## Set name disbled
            self.user_name.setDisabled(1)
            self.login_btn.setDisabled(1)

            ## Call disabled
            self.dc.setDisabled(0)
            self.call_btn.setDisabled(0)
            self.user_to_call.setDisabled(0)
        


    def connect(self):
        self.client.connect_to_server(self.ip.text())
    def disconnect(self):
        self.client.logoff()

    def login(self):
        self.client.login(self.user_name.text())

    def call(self):
        self.client.call_user(self.user_to_call.text())
    def end_call(self):
        self.client.end_call()
   
    def call_request_pop_up(self):
        p = CallPopUp(self.client.name,self)
        return p.exec_()


class VoiceRecorder():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    audio = pyaudio.PyAudio()

    def __init__(self, cliente: Client) -> None:
        self.client = cliente
        self.client.on_voice_receive = self.play_voice

        self.streamin = self.audio.open(format=self.FORMAT, 
                    channels=self.CHANNELS, 
                    rate=self.RATE, 
                    input=True, 
                    frames_per_buffer=self.CHUNK)

        self.streamout = self.audio.open(format=self.FORMAT, 
                    channels=self.CHANNELS, 
                    rate=self.RATE, 
                    output=True, 
                    frames_per_buffer=self.CHUNK)

    def record_voice(self) -> bytes:
        if self.client._udp_state == "on_call":
            return self.streamin.read(1024)

    def record_and_send(self):
        while 1:
            data = self.record_voice()
            if data:
                self.client.send_voice(data)

    def play_voice(self, voice: bytes):
        self.streamout.write(voice)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()

    ####
    vc = VoiceRecorder(window.client)
    # criar uma thread de um metodo de vc que checa o estado do client_udp. Se for on call, captura e manda voz
    thread(vc.record_and_send, ())
    # criar um callback e tacar dentro da função received_voice, e dentro desse call back ele toca a voz pro usuário
    ####
    
    sys.exit(app.exec_())
