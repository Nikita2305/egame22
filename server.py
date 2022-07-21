from django.forms import ModelForm
from backend.model import Model
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
import asyncio
import websockets
import json
import jsonpickle

admin_tokens=[]
team_tokens=[]

methods_list=[]
admin_methods=["save","print_log"]

Model()


with open("admin_tokens.secret","r") as f:
    admin_tokens=[line.strip("\n ") for line in f]

with open("team_tokens.secret","r") as f:
    team_tokens=[line.strip("\n ") for line in f]

def reply(code,msg,token):
    return json.dumps({"msg":msg,"code":code,"token":token});



async def igra(websocket):
    async for message in websocket:
        print(message)
        req=[]
        token,method,args,kwargs="","",[],{}
        
        try:
            req=json.loads(message)
        except Exception as e:
            print(e)
            await websocket.send(reply(1337,"bad request",token))
            continue

        if "token" not in req:
            await websocket.send(reply(1337,"no token provided",token))
            continue
        else: token=req["token"]

        if token not in admin_tokens and token not in team_tokens:
            await websocket.send(reply(1337,"shitty token",token))
            continue

        if ("method" not in req) or not '''(req["method"] not in methods_list)''':
            await websocket.send(reply(1337,"no/nonexistent token sent",token))
            continue
        else: method=req["method"]

        if method in admin_methods and token not in admin_tokens:
            await websocket.send(reply(1337,"method requires admin priviliges",token))
            continue
        
        if "args" in req:
            args=req["args"]
        
        if "kwargs" in req:
            kwargs=req["kwargs"]

        await websocket.send(reply(200,"OK",token))

async def main():
    async with websockets.serve(igra, port=1337):
        await asyncio.Future()  # run forever

asyncio.run(main())