import asyncio
import websockets
import json

token="TOKEN1"
# with open("admin_tokens.secret") as f:
#     token=f.read().strip("\n ")

async def get_and_format_input():
    global token
    method=input("Method: ")
    args=input("Args split by ',': ").split(",")
    kwargs=json.loads(input("Kwargs as a dict: "))
    return f'{{"token":"{token}","method":"{method}","args":{json.dumps(args)},"kwargs":{json.dumps(kwargs)}}}'

async def cli():
    async for websocket in websockets.connect("ws://localhost:1337/",ping_interval=None):
        try:
            msg = await get_and_format_input()
            print(msg)
            await websocket.send(msg)
            print(await websocket.recv())
        except websockets.ConnectionClosed:
            continue

asyncio.run(cli())

