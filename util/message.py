import json

class Message:
    MESSAGE_TYPES = [
        "\0",   #NOTE Avoid using null terminator by accident
        "unexpected_message",
        "register",
        "accepted_register",
        "declined_register",
        "registry",
        "not_found",
        "call_request",
        "reject_call",
        "accept_call",
        "occupied",
        "voice",
        "end_call",
        "unregister",
        "accepted_unregister",
        "users_list"
    ]

    def __init__(self, type: bytes, **kwargs):
        if isinstance(type, str): 
            type = Message.kind(type)
        self.type = type
        self.info = kwargs

    def __str__(self) -> str:
        return(
            Message.kind(self.type) + '\n' + 
            json.dumps(self.info, sort_keys=True, indent=3))

    def __repr__(self) -> str:
        return(
            Message.kind(self.type) + '; ' + 
            json.dumps(self.info, sort_keys=True))

    def kind(t):
        if isinstance(t, str):
            return bytes([Message.MESSAGE_TYPES.index(t)])

        elif isinstance(t, bytes) and len(t) == 1:
            return Message.MESSAGE_TYPES[int(t[0])]

        elif isinstance(t, int):
            return Message.MESSAGE_TYPES[t]

        raise Exception(
            f"Message type must be either a single byte, a string or an int. Got {type(t)}" + 
            ["", f" of length {len(t)}"][isinstance(t, bytes)]
        )
    
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
        return self.type + json.dumps(self.info).encode()

    def decode(data: bytes):
        try:
            type = data[0]
            info = json.loads(data[1:])
            return Message(type=bytes([type]), **info)

        except Exception as e:
            print(e)
            return None