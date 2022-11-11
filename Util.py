import json

class Callable():
    def __init__(self, func, **kwargs) -> None:            
        self.func = func
        self.kwargs = kwargs

    def __call__(self, *args, **kwds):
        return self.func(*args, **self.kwargs, **kwds)

class Message:
    Message_types = [
        "\0",## Avoid using null terminator by accident
        "unexpected_message"
        "register","accepted_register","declined_register","registry","not_found",
        "call_request","reject_call","accept_call","occupied"
        "voice_packet","end_call"
        ]


    def __init__(self, t: bytes, **kwargs):
        if isinstance(t, str):
            t = Message.kind(t)
        self.t = t
        self.info = kwargs

    def __str__(self) -> str:
        return(Message.kind(self.t) + '\n' + json.dumps(self.info, sort_keys=True, indent=3))
    def __repr__(self) -> str:
        return(Message.kind(self.t) + '\n' + json.dumps(self.info, sort_keys=True))

    def kind(t):
        if isinstance(t, str):
            return bytes([Message.Message_types.index(t)])
        elif isinstance(t, bytes) and len(t) == 1:
            return Message.Message_types[int(t[0])]
        elif isinstance(t, int):
            return Message.Message_types[t]
        
        raise Exception(f"Message type must be either a single byte, a string or an int. Got {type(t)}" + ["",f" of length {len(t)}"][isinstance(t, bytes)])
    
    ### Get attributes that aren't defined.
    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except:
            try:
                return self.info[__name]
            except Exception as e:
                # print(f"[Warning] No attribute named {__name} for {self}. The message might not be following the message.type formatting proprelly.")
                return None

    def encode(self) -> bytes:
        return self.t + json.dumps(self.info).encode()
    def decode(_o: bytes, from_addrs=None):
        try:
            t = _o[0]
            info = json.loads(_o[1:])

            return Message(t=bytes([t]), from_addrs=from_addrs, **info)
        except Exception as e:
            print(e)
            return None

class WSocket():
    def __init__(self, socket) -> None:
        self.socket = socket
        self.buffered_message = []

    def send(self, msg: Message, *args, **kwargs):
        self.socket.send(msg.encode() + b'\0', *args, **kwargs)

    def recv(self, *args, **kwargs) -> Message:
        if self.buffered_message == []:
            data = self.socket.recv(*args, **kwargs)
            self.buffered_message += data.split(b'\0')[:-1]

        ## Try to decode. If it fails, message is broken, so ignore it.
        msg = self.buffered_message.pop(0)
        try:
            msg.decode()
        except:
            return self.recv( *args, **kwargs) ## Ignore and try again
        return msg ## Decoded correctly

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except:
            return self.socket.__getattribute__(__name)
