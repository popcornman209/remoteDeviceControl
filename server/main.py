from websockets.asyncio.server import serve
import asyncio, json, os, shutil

if not os.path.exists("config.json"):
    shutil.copyfile("config.default.json", "config.json")
with open("config.json", "r") as f:
    config = json.load(f)


# main hanlder for clients
async def handler(websocket):
    print(await websocket.recv())
    await websocket.send("greg")


async def main():
    async with serve(handler, "", config["port"], compression=None):
        await asyncio.Future()

if __name__ == "__main__": asyncio.run(main())