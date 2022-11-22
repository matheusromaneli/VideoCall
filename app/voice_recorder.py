from app.client import Client
import pyaudio

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