from glob import glob
from django.forms import ModelForm
from backend.model import Model
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.graph import Graph
from backend.market import Market, BaseTrend
from backend.newsfeed import NewsFeed
from backend.teams import Team, TeamsManager
from backend.war import WarManager, War
import asyncio
import websockets
import json
import jsonpickle
from random import randint

admin_tokens=[]
team_tokens=[]

currencies_list=["BTC_1","BTC_2"]
methods_list=[]
admin_methods=["save","print","on_bot_connect", "register_team"]


#-=-=-=-=-=-=-=-=-=-=-=-(GAVNO(+-100проц будет переписано))=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Model.GetInstance()
Model.GetInstance().market_=Market(10,dict([(c,BaseTrend(1000,100,abs(hash(c)))) for c in currencies_list]))
Model.GetInstance().teams_=TeamsManager(currencies_list)
Model.GetInstance().graph_=Graph(10,Model.GetTeams())
Model.GetInstance().news_feed_=NewsFeed(["2ch","4chan","habr"])

#-=-=-=-=-=-=-=-=-=-=-=-(/GAVNO(+-100проц будет переписано))-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

with open("admin_tokens.secret","r") as f:
    admin_tokens=[line.strip("\n ") for line in f]

with open("team_tokens.secret","r") as f:
    team_tokens=[line.strip("\n ") for line in f]

def reply(code,msg,token,data=None):
    if(data!=None):
        return json.dumps({{"msg":msg,"code":code,"token":token,"data":data}})
    return json.dumps({"msg":msg,"code":code,"token":token});

#-=-=-=-=-=-=-=-=-=-=-=-(METHODS)=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def save():
    pass #saves gamestate

async def printt():
    pass #prints gamestate

async def register_team(websocket, token, team_name):
    Model.AcquireLock();
    Model.GetTeams().CreateTeam("TOKEN_"+str(randint(1,100500)),team_name)
    Model.ReleaseLock();
    await websocket.send(reply(200,"Team "+team_name+" registered",token))

# async def give_crypto(websocket, team_token, )

# async def give_money(websocket, team_token, t)
async def on_bot_connect(websocket, token):
    await websocket.send(reply(200,"OK",token,currencies_list))
    return

async def sell(websocket,name,amount):
    Model.AcquireLock();
    if Model.GetTeams().GetTeamByName(name).GetCryptoMoney():
        pass

async def buy(websocket,name,amount):
    pass

async def change_node(node_id, new_state):
    pass

# async def 

#-=-=-=-=-=-=-=-=-=-=-=-(/METHODS)-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

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

        if method=="ONCONNECT":
            await on_bot_connect()
        elif method=="print":
            await printt()
        # elif method=="CHANGE_MODE":
        #     await change_mode()
        elif method=="BUY":
            await buy()
        elif method=="register_team":
            await register_team(websocket,token,args[0])
        else:
            await websocket.send(reply(228,"Something really weird happened",token))

async def main():
    async with websockets.serve(igra, port=1337):
        await asyncio.Future()  # run forever

asyncio.run(main())