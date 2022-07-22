from glob import glob
from django.forms import ModelForm
from backend.model import Model
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.graph import Graph
from backend.server import Server
from backend.market import Market, BaseTrend
from backend.newsfeed import NewsFeed
from backend.teams import Team, TeamsManager
from backend.war import WarManager, War
from backend.wheels.utils import GraphGenerator
import asyncio
import websockets
import json
import jsonpickle
from random import randint

admin_tokens=[]
team_tokens=[]

methods_list=[]
admin_methods=["save","print","on_bot_connect", "register_team", "subscribe_leaderboard","post"]


#-=-=-=-=-=-=-=-=-=-=-=-(GAVNO(+-100проц будет переписано))=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

currencies_list=["SigmaCoin","Kefirium","DogeCoin","AttendenceCoin"]
cur_bases = dict([(c,BaseTrend(100,10,abs(hash(c)))) for c in currencies_list])
class AttendancePrice:
    def __init__(self):
        self.cache_ = [62,61,60,57,51,55,49,56,47,47]
    def __call__(self, x):
        if x < len(self.cache_):
            return self.cache_[x]
        else:
            return self.cache_[-1] - (x-len(self.cache_)) if self.cache_[-1] - (x-len(self.cache_)) > 0 else 1
cur_bases["AttendenceCoin"] = AttendancePrice()
Model.GetInstance()
Model.GetInstance().market_=Market(60,cur_bases)
Model.GetInstance().teams_=TeamsManager(currencies_list)
nteams = 8;
colors = [
    "#4281A4",
    "#080357",
    "#FF6B6B",
    "#F8F4A6",
    "#BDF7B7",
    "#37DB25",
    "#F1A6F7",
    "#1D1D1D"
    ]

for i in range(nteams):
    Model.GetTeams().CreateTeam("TOKEN"+str(i+1),None,colors[i])

Model.GetInstance().graph_=Graph(120,Model.GetTeams(),currencies_list)
vv,ee = GraphGenerator(nteams=nteams,
                   n_outer_ring_vert_per_team=12, 
                   n_core_vert_per_team=4,
                   n_outer_edges=20,
                   n_core_edges=3,
                   n_links=4,
                   debug=False)
servers = []
for v in vv:
    s = Server(Model.GetGraph(), v.i)
    s.set_x(v.x)
    s.set_y(v.y)
    s.set_power(v.power)
    servers.append(s)
for e in ee:
    Model.GetGraph().add_edges(servers[e[0].i], [servers[e[1].i]])
    
tl = Model.GetTeams().GetTeamsList()
for i in range(len(tl)):
    servers[i*16].set_owner(tl[i])

Model.GetInstance().wars_ = WarManager(servers,120)

Model.GetInstance().events_ = EventManager()

Model.GetInstance().news_feed_=NewsFeed(["2ch","4chan","habr"])
Model.Run()

#-=-=-=-=-=-=-=-=-=-=-=-(/GAVNO(+-100проц будет переписано))-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

with open("admin_tokens.secret","r") as f:
    admin_tokens=[line.strip("\n ") for line in f]

with open("team_tokens.secret","r") as f:
    team_tokens=[line.strip("\n ") for line in f]

def reply(code,msg,token,data=None):
    if(data!=None):
        return json.dumps({"msg":msg,"code":code,"token":token,"data":data})
    return json.dumps({"msg":msg,"code":code,"token":token});

def sub_reply(code,msg,token):
    return json.dumps({"crypto_currencies":[{"name":"fuckyou","price":0}]})
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

async def give_crypto(websocket, token, team_name, cur, amount):
    Model.AcquireLock()
    Model.GetTeams().GetTeamByName(team_name).AddCryptoMoney(cur,float(amount),"admin")
    Model.ReleaseLock()
    await websocket.send(reply(200,"Added crypto",token))

async def give_dollar(websocket, token, team_name, amount):
    Model.AcquireLock()
    Model.GetTeams().GetTeamByName(team_name).AddMoney(float(amount),"admin")
    Model.ReleaseLock()
    await websocket.send(reply(200,"Added dollar",token))

# async def print_team

async def transfer_money(websocket, token, team2, cur, amount):
    Model.AcquireLock()
    t1,t2=Model.GetTeams().GetTeam(token),Model.GetTeams().GetTeamByName(team2);
    if(cur=="dollar"):
        if(t1.AddMoneyCheck(-amount)):
            t1.AddMoney(-amount)
            t2.AddMoney(amount)
        else:
            await websocket.send(reply(228,"Not enough dollars",token))
            Model.ReleaseLock()
            return
    if(cur in currencies_list):
        if(t1.AddCryptoCheck(cur,-amount)):
            t1.AddCrypto(-amount)
            t2.AddCrypto(amount)
        else:
            await websocket.send(reply(228,"Not enough dollars",token))
            Model.ReleaseLock()
            return
    Model.ReleaseLock()
    await websocket.send(reply(200,"Transfer successful",token))

# async def give_money(websocket, team_token, t)
async def on_bot_connect(websocket, token):
    await websocket.send(reply(200,"OK",token,{"teams":Model.GetTeams().GetTeamsNames(),"forums":[]}))
    
async def sell(websocket,name,amount):
    Model.AcquireLock();
    if Model.GetTeams().GetTeamByName(name).GetCryptoMoney():
        pass

async def buy(websocket,name,amount):
    pass

async def change_node(node_id, new_state):
    pass

async def subscribe_leaderboard(websocket, token):
    def teams(r):
        print("puk")
        asyncio.run(websocket.send(sub_reply(3,"TEAM UPD",1)))
        print("kak")
    def market(r):
        print("puk")
        asyncio.run(websocket.send(sub_reply(1,"MARKET_UPD",3)))
        print("kak")
    Model.AcquireLock()
    [Model.AddSubscription(Subscription(team,teams)) for team in Model.GetTeams().GetTeamsList()]
    Model.AddSubscription(Subscription(Model.GetMarket(),market))
    Model.ReleaseLock()
    await websocket.send(reply(200,"Succsesfull subscribe",token))
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

        if ("method" not in req):
            await websocket.send(reply(1337,"no method sent",token))
            continue
        else: method=req["method"]

        # if method in admin_methods and token not in admin_tokens:
        #     await websocket.send(reply(1337,"method requires admin priviliges",token))
        #     continue
        
        if "args" in req:
            args=req["args"]
        
        if "kwargs" in req:
            kwargs=req["kwargs"]

        if(method in globals()):
            await globals()[method](websocket,token,*args,**kwargs)
        else:
            await websocket.send(reply(228,"No such method",token))

async def main():
    async with websockets.serve(igra, port=1337, ping_interval=None):
        await asyncio.Future()  # run forever

asyncio.run(main())
