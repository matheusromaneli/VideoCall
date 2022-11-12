from Client import Client
from time import sleep
from Util import *

c = Client()

sleep(0.4)
c.send(Message("register", user_name=input("Your name: "), udp_address="0.0.0.0:0"))


sleep(0.4)
c.send(Message("registry", user_name="Bruno"))

while 1:
    pass