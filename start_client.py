import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from util.thread import thread
from app.voice_recorder import VoiceRecorder
from app.window import Window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()

    ####
    vr = VoiceRecorder(window.client)
    # criar uma thread de um metodo de vc que checa o estado do client_udp. Se for on call, captura e manda voz
    thread(vr.record_and_send, ())
    # criar um callback e tacar dentro da função received_voice, e dentro desse call back ele toca a voz pro usuário
    ####
    
    sys.exit(app.exec_())