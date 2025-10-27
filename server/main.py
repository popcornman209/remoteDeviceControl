from websockets.asyncio.server import serve
from discord_webhook import DiscordWebhook
import asyncio, json, os, shutil, traceback

if not os.path.exists("config.json"):
    shutil.copyfile("config.default.json", "config.json")
with open("config.json", "r") as f:
    config = json.load(f)


# main hanlder for clients
async def handler(websocket):
    try:
        print(await websocket.recv())
        await websocket.send("greg")
        0/0
    except Exception as e:
        message = f"Error: {e}\n\n{traceback.format_exc()}"
        print(f"==========Error==========\n{message}\n=========================")
        if config["discord_webhook"] != "":
            webhook = DiscordWebhook(url=config["discord_webhook"], content=f"Server Error! {config["discord_ping"]}\n```\n{message}\n```")
            webhook.execute()

async def main():
    async with serve(handler, "", config["port"], compression=None):
        await asyncio.Future()

if __name__ == "__main__": asyncio.run(main())