from ast import Mod
from glob import glob
from django.forms import ModelForm
from backend.model import Model
from backend.text_generation.posting import Floodilka
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.graph import Graph
from backend.server import Server
from backend.market import Market, BaseTrend
from backend.newsfeed import NewsFeed
from backend.teams import Team, TeamsManager
from backend.war import WarManager, War
from backend.wheels.utils import GraphGenerator
from backend.events import EventManager
import asyncio
import websockets
import json
import jsonpickle
from random import randint

admin_tokens=[]
team_tokens=[]

methods_list=[]
admin_methods=["save","print","on_bot_connect", "register_team", "subscribe_leaderboard", "post", "launch_event"]
forums=["2ch","4chan","habr"]

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
Model.GetInstance().market_=Market(5,cur_bases)
Model.GetInstance().teams_=TeamsManager(currencies_list)
nteams = 8;
colors = [
    "#1d85e8",
    "#f88d2c",
    "#5451b0",
    "#db6656",
    "#42a18a",
    "#30779d",
    "#ee4a5d",
    "#ef9cf0"
    ]

for i in range(nteams):
    Model.GetTeams().CreateTeam("TOKEN"+str(i+1),colors[i])

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

Model.GetInstance().news_feed_=NewsFeed(forums)
# for name in forums:
#     Model.ScheduleRoutine(Routine(Floodilka(name),1))


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

async def give(websocket, token,team_name,cur,amount):
    if(cur=="dollar"):
        await give_dollar(websocket,token,team_name,amount)
    elif(cur in currencies_list):
        await give_crypto(websocket,token,team_name,cur,amount)
    else:
        await websocket.send(reply(228,"HEHEH",token))

async def info(websocket,token):
    await websocket.send(reply(200,"OK",token,json.dumps({"name":Model.GetTeams().GetTeam(token).GetName(),"money":[{"name":"dollar","amount":Model.GetTeams().GetTeam(token).GetMoney()}]+[{"name":cur,"amount":Model.GetTeams().GetTeam(token).GetCryptoMoney(cur)} for cur in currencies_list],"nodes":[{"id":node.get_id(),"state":node.get_type(),"power":node.get_power()} for node in Model.GetGraph().get_servers_by_owners(Model.GetTeams().GetTeam(token))]})))

# async def upgrade(websocket,token,node_id):
#     Model.AcquireLock()
#     if(Model.GetTeams().GetTeam(token).AddMoneyCheck(-Model.GetGraph().find_server(id)))
#     Model.GetGraph().upgrade_server(node_id,Model.GetGraph().find_server(id).get_power()*1.5)

# async def print_team

async def launch_event(websocket, token, event_name):
    Model.AcquireLock()
    ok = True
    try:
        Model.GetEventManager().LoadEvent(event_name)
        Model.GetEventManager().LaunchEvent(event_name)
    except:
        ok = False
    finally:
        Model.ReleaseLock()

    if ok:
        await websocket.send(reply(200,"OK",token))
    else:
        await websocket.send(reply(228,"error",token))

async def stop_event(websocket, token, event_name):
    Model.AcquireLock()
    ok = True
    try:
        Model.GetEventManager().StopEvent(event_name)
    except:
        ok = False
    finally:
        Model.ReleaseLock()

    if ok:
        await websocket.send(reply(200,"OK",token))
    else:
        await websocket.send(reply(228,"error",token))

async def transfer(websocket, token, team2, cur, amount):
    amount=float(amount)
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
        if(t1.AddCryptoMoneyCheck(cur,-amount)):
            t1.AddCryptoMoney(cur,-amount)
            t2.AddCryptoMoney(cur,amount)
        else:
            await websocket.send(reply(228,"Not enough dollars",token))
            Model.ReleaseLock()
            return
    Model.ReleaseLock()
    await websocket.send(reply(200,"Transfer successful",token))

# async def give_money(websocket, team_token, t)
async def on_bot_connect(websocket, token):
    await websocket.send(reply(200,"OK",token,{"teams":Model.GetTeams().GetTeamsNames(),"forums":forums,"currencies":currencies_list}))
    
async def sell(websocket,token,cur,amount):
    amount=float(amount)
    Model.AcquireLock();
    if Model.GetTeams().GetTeam(token).AddCryptoMoneyCheck(cur,-amount):
        Model.GetTeams().GetTeam(token).AddMoney(amount*Model.GetMarket().GetExchangeRate(cur))
        Model.GetTeams().GetTeam(token).AddCryptoMoney(cur,-amount)
        Model.ReleaseLock()
        await websocket.send(reply(200,"Crypto exchanged",token))
    else:
        Model.ReleaseLock()
        await websocket.send(reply(228,"Not enough crypto",token))


async def remove_node(websocket, token, node_id):
    Model.AcquireLock()
    Model.GetGraph().find_server(node_id).turn_off()
    Model.ReleaseLock()
    
    await websocket.send(reply(200,"OK",token))


async def buy(websocket,token,cur,amount):
    amount=float(amount)
    Model.AcquireLock();
    if Model.GetTeams().GetTeam(token).AddCryptoMoney(-amount):
        Model.GetTeams().GetTeam(token).AddMoney(amount/Model.GetMarket().GetExchangeRate(cur))
        Model.GetTeams().GetTeam(token).AddCryptoMoney(-amount)
        Model.ReleaseLock()
        await websocket.send(reply(200,"Crypto exchanged",token))
    else:
        Model.ReleaseLock()
        await websocket.send(reply(228,"Not enough crypto",token))

async def reclassify(websocket, token, node_id, new_state):
    Model.AcquireLock()
    if node_id not in [node.get_id() for node in Model.GetGraph().get_servers_by_owners(Model.GetTeams().GetTeam(token))]:
        return await websocket.send(reply(208,"not your node",token))

    if not Model.GetTeams.GetTeam(token).AddActionsCheck(-1):
        return await websocket.send(reply(209,"not enough actions",token))
    
    Model.GetGraph().find_server(node_id).set_type(new_state)
    Model.GetTeams.GetTeam(token).AddActions(-1)

    Model.ReleaseLock()

    await websocket.send(reply(200,"OK",token)) 

async def subscribe_leaderboard(websocket, token):
    def teams(r):
        print("team callback triggered")
        asyncio.run(websocket.send(json.dumps({"teams":[{"name":team.GetName(),"color":team.GetColor(),"balance":team.GetMoney()} for team in Model.GetTeams().GetTeamsList()]})))
    def market(r):
        print("market callback triggered")
        asyncio.run(websocket.send(json.dumps({"crypto_currencies":[{"name":x,"price":y} for x,y in ((name,Model.GetMarket().GetExchangeRate(name)) for name in currencies_list)]})))
    Model.AcquireLock()
    [Model.AddSubscription(Subscription(team,teams)) for team in Model.GetTeams().GetTeamsList()]
    Model.AddSubscription(Subscription(Model.GetMarket(),market))
    asyncio.create_task(websocket.send(json.dumps({"teams":[{"name":team.GetName(),"color":team.GetColor(),"balance":team.GetMoney()} for team in Model.GetTeams().GetTeamsList()]})))
    asyncio.create_task(websocket.send(json.dumps({"crypto_currencies":[{"name":x,"price":y} for x,y in ((name,Model.GetMarket().GetExchangeRate(name)) for name in currencies_list)]})))
    Model.ReleaseLock()
    await websocket.send(reply(200,"Succsesfull subscribe",token))

async def subscribe_graph(websocket, token):
    def form_json():
        return json.dumps(
                    {
                        "nodes":[{"id":node.get_id(),"positionX":node.get_x(),"positionY":node.get_y(),"power":node.get_power(),"defense":node.get_power()*node.get_k(),"type":node.get_type(),"level":node.get_level(),"color":node.get_owner().GetColor() if node.get_owner() is not None else None} for node in Model.GetGraph().get_vertexes()],
                        "edges":[{"source":e[0],"target":e[1]} for e in Model.GetGraph().get_edges()],
                        "timers":[{"source":w.get_attaker(),"target":w.get_defender(),"timer":Model.GetWarManager().get_war_routine(w).GetRemainingTime()} for w in Model.GetWarManager().get_wars()]
                    })
    Model.AcquireLock()
    asyncio.create_task(websocket.send(form_json()))
    Model.ReleaseLock()
    class graph(Executable):
        def __init__(self):
            super().__init__()
            self.sub = None
        def __call__(self,r):
            print("graph callbakc triggered")
            if websocket.closed and self.sub is not None:
                Model.AcquireLock()
                Model.EraseSubscription(self.sub)
                Model.ReleaseLock()
            else:
                Model.AcquireLock()
                asyncio.run(websocket.send(form_json()))
                Model.ReleaseLock()
    
    Model.AcquireLock()
    G = graph()
    S = Subscription(Model.GetGraph(),G)
    G.sub = S
    Model.AddSubscription(S)
    Model.ReleaseLock()
    await websocket.send(reply(200,"successfull subscribe",token))

async def subscribe_forum(websocket,token,forum):
    asyncio.create_task(websocket.send(json.dumps({"posts":[{"name":post.GetHeader(),"text":post.GetBody(),"author":post.GetAuthor()} for post in Model.GetNewsFeed().GetPosts(forum)]})))
    def forumm(r):
        print("forum callback triggered")
        asyncio.run(websocket.send(json.dumps({"posts":[{"name":post.GetHeader(),"text":post.GetBody(),"author":post.GetAuthor()} for post in Model.GetNewsFeed().GetPosts(forum)]})))
    Model.AcquireLock()
    Model.AddSubscription(Subscription(Model.GetNewsFeed(),forumm))
    Model.ReleaseLock()
    await websocket.send(reply(200,"successfull subscribe",token))

async def post(websocket,token, forum, author, header, body):
    Model.AcquireLock()
    Model.GetNewsFeed().SendPost(forum, author, header, body)
    Model.ReleaseLock()
    await websocket.send(reply(200,"post posted",token))

async def get_posts(websocket,token,forum):
    await websocket.send(reply(200,"posts acuireseded",token,[{"name":post.GetHeader(),"text":post.GetBody(),"author":post.GetAuthor()} for post in Model.GetNewsFeed().GetPosts(forum)]))

async def attack(websocket,token,id_from,id_to):
    Model.AcquireLock()
    Model.GetWarManager()
    Model.ReleaseLock()

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
    async with websockets.serve(igra, port=1337):
        await asyncio.Future()  # run forever

asyncio.run(main())
