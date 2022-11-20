from util.user import User

class ConnectionTable():
    def __init__(self, connections = []):
        self.active_connections = connections

    def find_by(self, key, value):
        for connection in self.active_connections:
            if connection.__getattribute__(key) == value:
                return connection

    def __iter__(self):
        return iter(self.active_connections)

    def append(self, user: User):
        self.active_connections.append(user)
        print(table(["Name", "Ip", "Porta"], self.listfy()))

    def remove(self, user: User):
        self.active_connections.remove(user)

    def jsonfy(self):
        return {"users": [x.jsonfy() for x in self.active_connections]}

    def listfy(self):
        return [[x.name, x.ip, x.porta] for x in self.active_connections]