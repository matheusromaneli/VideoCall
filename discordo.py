# from socket import socket as Socket
# import socket
# from threading import Thread
# import json




# class Client:
#     def __init__(self, ip='localhost', port=11111, on_message = lambda *args, **kwargs: None, _socket=None, should_thread=True):
#         if _socket != None:
#             self.s = _socket
#         else:
#             self.s = WSocket(Socket(family=socket.AF_INET, type=socket.SOCK_STREAM))
#             print("connecting")
#             self.s.connect((ip,port))
#             print("connected")


#         self.on_message = on_message

#         self.online = 1
#         if should_thread:
#             thread(self.listen_to_server, ())

#     def start(self, *args):
#         thread(self.listen_to_server, *args)

#     def send(self, msg: Message):
#         if isinstance(msg, bytes):
#             self.s.send(msg)
#         else:
#             self.s.send(msg.encode())

#     @logger
#     def receive(self, msg: Message):
#         if msg == None:
#             return
#         self.on_message(msg)

#     def listen_to_server(self):
#         while self.online:
#             data = self.s.recv(1024)
#             self.receive(Message.decode(data))


# class User:
#     def __init__(self, id: int,  addrs: tuple, conn, name: str ="", on_message = lambda *args, **kwargs: None) -> None:
#         self.id = id
#         self.name = name
#         self.socket = Client(_socket=conn, on_message= self.receive)
#         self.addrs = addrs
#         self.on_message = on_message

#     def send(self, msg: Message):
#         self.socket.send(msg)


#     @logger
#     def receive(self, msg: Message):
#         if msg == None:
#             return
#         self.on_message(msg)


# class Client_Room:
#     def __init__(self, name, users, tcp_addrs, udp_addrs=None, on_message = lambda *args, **kwargs: None, password=None):

#         self.tcp_socket = WSocket(socket.create_connection(tuple(tcp_addrs)))
#         self.udp_socket = WSocket(Socket(family=socket.AF_INET, type=socket.SOCK_DGRAM))
#         self.udp_socket.bind(("",0))

#         if udp_addrs == None:
#             self.tcp_socket.send(Message(Message.kind("join_call"),password=password, udp_addrs=self.udp_socket.getsockname()).encode())
#             udp_message = Message.decode(self.tcp_socket.recv(1024))
#             udp_addrs = tuple(udp_message.udp_addrs)
#         # self.udp_socket.sendto(Message(Message.kind("connecting!")).encode(),udp_addrs)

#         self.on_message = on_message

#         self.name = name
#         self.users = users

#         self.udp_addrs = udp_addrs
#         self.tdp_addrs = tcp_addrs


#         thread(self.tcp_listen, ())
#         thread(self.udp_listen, ())

#     @logger
#     def receive(self, msg: Message, tcp_udp: int):
#         if msg == None:
#             return
#         self.on_message(msg)

#     def send_tcp():
#         pass
#     def send_udp():
#         pass

#     def tcp_listen(self):
#         while 1:
#             data = self.tcp_socket.recv(1024)
#             self.receive(Message.decode(data), tcp_udp=0)

#     def udp_listen(self):
#         while(1):
#             data = self.udp_socket.recvfrom(1024)
#             print(data)

#             for msg in data.split(b"\0")[:-1]:
#                 self.receive(
#                     Message(
#                         Message.kind("voice_pack"),
#                         id=msg[0],
#                         voice=msg[1:],
#                         ),
#                     tcp_udp=1
#                 )

# class Server_Room:
#     def __init__(self, name, public=1, password=None, users=[], ip='localhost', on_message = lambda *args, **kwargs: None):
#         self.tcp_socket = WSocket(Socket(family=socket.AF_INET, type=socket.SOCK_STREAM))
#         self.udp_socket = WSocket(Socket(family=socket.AF_INET, type=socket.SOCK_DGRAM))
#         self.tcp_socket.bind((ip,0))
#         self.udp_socket.bind((ip,0))

#         self.users = users
#         self.name = name
#         self.public = public
#         self.password = password
#         self.on_message = on_message

#         thread(self.tcp_connect, ())
#         # thread(self.udp_connect, ())

#     def jsonfy(self):
#         return {
#             'name':self.name,
#             'users':[y.name for y in self.users],
#             'tcp_addrs':self.tcp_socket.getsockname()
#         }

#     @logger
#     def receive(self, msg: Message, tcp_udp: int, conn: WSocket):
#         if msg == None:
#             return

#         if tcp_udp == 0 and msg.t == Message.kind("join_call"):
#             if (
#                 self.password == None or msg.password == self.password 
#                     and
#                 msg.user not in self.users
#                 ):
#                 conn.send(
#                     Message(
#                         Message.kind("udp_info"),
#                         udp_addrs=self.udp_socket.getsockname()
#                         ).encode()
#                     )

#         ## If msg is udp and is "voice", send to all other users trough udp (using self.users[x][1])

#         self.on_message(msg)

#     def tcp_connect(self):
#         self.tcp_socket.listen()
#         while (1):
#             conn, addr = self.tcp_socket.accept()
#             conn = WSocket(conn)
#             self.users.append([conn])
#             self.user_joined("user")
#             thread(self.tcp_listen, (conn, "user"))


#     def tcp_listen(self, conn: WSocket, user_name):
#         try:
#             data = conn.recv(1024)
#             udp_msg = Message.decode(data)


#             if udp_msg.t != Message.kind("udp_address"):
#                 conn.send(Message("not_ok_bro",0,message="An UDP address must be informed as the first information sent to the server."))
#                 self.user_left(user_name)
#                 self.users[i] == [None, None]
#                 return

#             i=0
#             for user in self.users:
#                 if user[i][0] == conn:
#                     self.users[i].append(udp_msg.udp_address)
#                 i+=1
                            
#             while 1:
#                 data = conn.recv(1024)
#                 self.receive(Message.decode(data), tcp_udp=0, conn=conn)
#         except:
#             self.user_left(user_name)
#             self.users[i] == [None, None]

#     def udp_listen(self):
#         ## Receive data from socket
#         ## Check if the address is in self.users (self.users = [[tcp: WScoket, udp: str], [...], ...])
#         ## If it is, decode Message and send to self.receive(msg, tcp_udp=1, conn=conn)
#         pass

#     def send_user_tcp(self, msg: Message, user):
#         user.send(msg)
#     def send_users_tcp(self, msg: Message, users):
#         for user in users:
#             self.send_user_tcp(msg, user[0])

#     def user_joined(self, user_name):
#         self.send_users_tcp(Message("user_joined",0,user_name=user_name))
#     def user_left(self, user_name):
#         self.send_users_tcp(Message("user_left",0,user_name=user_name))

# class Rooms:
#     active = [Server_Room("General")]

#     def get_visbile_rooms() -> dict:
#         r = []
#         for x in Rooms.active:
#             if x.public:
#                 r.append(x.jsonfy())

#         return r

#     def create_room(name):
#         pass
#     def delete_room(name):
#         pass

#     def join(name,password=None):
#         pass

#     def get_room_by_name(name) -> Server_Room:
#         for room in Rooms.active:
#             if room.name == name and room.public:
#                 return room


# class Server:
#     def __init__(self, ip='localhost', port=11111, on_message=lambda *args, **kwargs: None) -> None:
#         self.s = socket.create_server((ip,port)) ## only redefined client_tcp, not server_tcp
#         self.s = WSocket(self.s)

#         self.addr = (ip,port)
#         self.on_message = on_message

#         self.online = 1

#         self.global_id = 1
#         self.users = []
#         self.rooms = Rooms

#         thread(self.wait_connections,())

#     def wait_connections(self):
#         self.s.listen()
#         while (1):
#             conn, addr = self.s.accept()
#             self.users.append(User(self.global_id,addr, WSocket(conn), on_message=Callable(self.receive, id=self.global_id)))
#             thread(self.client_thread, (WSocket(conn), self.global_id))

#             self.global_id+=1
    
#     @logger
#     def receive(self, msg: Message, id):
#         if msg == None:
#             return

#         self.on_message(msg)

#         if msg.t == Message.kind("room_info"):
#             room = self.rooms.get_room_by_name(msg.room_name)
#             if room == None:
#                 self.send(Message(Message.kind("not_ok_bro"), message=ServerResponses.Room_404), [id])
#             else:
#                 self.send(Message(Message.kind("room_info"), **room.jsonfy()))

#         elif msg.t == Message.kind("room_list"):
#             self.send(
#                 Message(
#                     t = Message.kind("room_list"),
#                     rooms = self.rooms.get_visbile_rooms()
#                     ),
#                 [id]
#             )

#         elif msg.t == Message.kind("join_call"):
#             room = self.rooms.get_room_by_name(msg.room_name)
#             if room == None:
#                 self.send(Message(Message.kind("not_ok_bro"), message=ServerResponses.Room_404), [id])
            
#             for x in room.users:
#                 if x.addrs == self.users[id].addrs:
#                     user = self.users[id]

#             if (
#                 room.password == None or msg.password == room.password 
#                     and
#                 user not in room.users
#                 ):
#                 self.send(Message(Message.kind("join_call"), **room.jsonfy()), [id])
#             else:
#                 self.send(Message(Message.kind("not_ok_bro"), message=ServerResponses.Room_403), [id])

#     def client_thread(self, conn: Socket, id):
#         self.send(
#             Message(
#                 t = Message.kind("room_list"),
#                 rooms = self.rooms.get_visbile_rooms()
#                 ),
#             [id]
#         )

#         while self.online:
#             data = conn.recv(1024)
#             for msg in data:
#                 self.receive(Message.decode(msg), id)


#     def send(self, message: Message, ids):
#         for id in ids:
#             user = self.users[id-1]
#             if user != None:
#                 user.socket.send(message.encode())