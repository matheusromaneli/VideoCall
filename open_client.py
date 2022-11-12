from Client import Client
from time import sleep
from Util import *

c = Client()
c.send(Message("register", user_name=input("Your name: "), ip=c.udp_address[0], porta=c.udp_address[1]))


def registry():
    user_name = input("What's the user's name?: ")
    c.send(Message("registry", user_name=user_name))

def call():
    user_name = input("Which User you want to call?: ")
    c.last_registry = None
    c.send(Message("registry", user_name=user_name))

    while c.last_registry == None:
        pass
    user_to_call = c.last_registry
    c.call(user_to_call['ip'], user_to_call['porta'])


options = ["Registry","Call","End Call"]
options_func = [registry, call, c.end_call]

while 1:
    if c.udp_state == "waiting_response":
        continue

    out = ""
    out += f"\n\n#### {c.udp_state}\n"
    for x in range(len(options)):
        out += f"{x+1}. {options[x]}\n"
    out += f"{x+2}. Exit\n"
    opt = input(out + "\nSelect your option: ")
    try:
        opt = int(opt)
    except:
        opt = None

    if opt != None and opt <= len(options) and opt >= 1:
        options_func[opt-1]()
    elif opt != None and opt == x+2:
        break
    else:
        print("Invalid option!")
    
    