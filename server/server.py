from websockets.asyncio.server import serve
import websockets.exceptions as wsErrors
from discord_webhook import DiscordWebhook
import asyncio, json, os, shutil, traceback

ignoredErrors = [
    wsErrors.ConnectionClosedOK,
    wsErrors.ConnectionClosedError
]
unImportantErrors = [
    json.decoder.JSONDecodeError
]

if not os.path.exists("config.json"):
    shutil.copyfile("config.default.json", "config.json")
with open("config.json", "r") as f:
    config = json.load(f)

if not config["password"]:
    print("No password set in config.json!, please input a password below, it will be eencrypted with sha256 and saved.")
    import getpass, hashlib
    password = getpass.getpass("Password: ")
    config["password"] = hashlib.sha256(password.encode()).hexdigest()
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    print("saved.")

clientList = []
controllerList = []

class clientObj():
    def __init__(self, name, host, features, ws):
        self.name = name
        self.host = host
        self.features = features
        self.busy = False
        self.ws = ws

        self.clientID = len(clientList)
        clientList.append(self)
        print(f"Client connected: {name}@{host} {ws.remote_address}")
    
    async def mainLoop(self):
        while True:
            message = await self.ws.recv()
            print(f"Message from {self.name}@{self.host}: {message}")

class conrollerObj():
    def __init__(self, ws):
        self.ws = ws

        self.controllerID = len(clientList)
        controllerList.append(self)
        print(f"Controller connected: {ws.remote_address}")
    
    async def mainLoop(self):
        while True:
            message = json.loads(await self.ws.recv())

            if message["command"] == "getClients":
                clients = [{"name": f"{client.name}@{client.host}", "id":client.clientID, "ip": client.ws.remote_address} for client in clientList if client != None]
                await self.ws.send(json.dumps(clients))

            if message["command"] == "getClient":
                clientID = message["id"]
                client = clientList[clientID]
                await self.ws.send(json.dumps({
                    "name": client.name,
                    "host": client.host,
                    "ip": client.ws.remote_address,
                    "features": client.features
                }))


# main hanlder for clients
async def handler(websocket):
    addr = websocket.remote_address
    try:
        clientInfo = json.loads(await websocket.recv())
        if clientInfo.get("type") == "client":
            client = clientObj(clientInfo.get("name"), clientInfo.get("host"), clientInfo.get("features"), websocket)
            await client.mainLoop()

        if clientInfo.get("type") == "controller":
            if clientInfo.get("password") != config["password"]:
                await websocket.send("error: Invalid password")
                await websocket.close()
                return
            controller = conrollerObj(websocket)
            await websocket.send("connected: Hello!")
            await controller.mainLoop()
        
    except Exception as e:
        if type(e) in ignoredErrors:
            print(f"Ignored error: {e} (IP: {addr})")
            return
        message = f"IP: {addr}\nError: {e}\n\n{traceback.format_exc()}"
        print(f"==========Error==========\n{message}\n=========================")
        if config["discord_webhook"] != "":
            webhook = DiscordWebhook(url=config["discord_webhook"], content=f"Server Error! {config["discord_ping"] if type(e) not in unImportantErrors else "(unimportant)"}\n```\n{message}\n```")
            webhook.execute()

async def main():
    async with serve(handler, "", config["port"], compression=None):
        await asyncio.Future()

if __name__ == "__main__": asyncio.run(main())