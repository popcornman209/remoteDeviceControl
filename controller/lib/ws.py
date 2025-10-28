import websocket, json

class ws:
    def __init__(self, address):
        self.address = address
        self.ws = websocket.WebSocket()
    
    def connect(self, passwd):
        self.ws.connect(self.address)
        self.ws.send(json.dumps({"type":"controller","password":passwd}))
        ack = self.ws.recv()
        return ack == "connected: Hello!"

    def getClients(self):
        self.ws.send(json.dumps({"command":"getClients"}))
        clients = json.loads(self.ws.recv())
        return clients
    
    def getClient(self, clientID):
        self.ws.send(json.dumps({"command":"getClient","id":clientID}))
        clientInfo = json.loads(self.ws.recv())
        return clientInfo