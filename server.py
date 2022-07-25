from ast import Mod
from glob import glob
import traceback
from backend.model import Model
from backend.wheels.routine import Executable, Routine, RepeatedRoutine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.graph import Graph
from backend.server import Server
from backend.market import Market, BaseTrend
from backend.newsfeed import NewsFeed
from backend.teams import Team, TeamsManager
from backend.war import WarManager, War
from backend.text_generation.posting import Floodilka
from backend.wheels.graph_generation import GraphGenerator
from backend.events import EventManager
from backend.callbacks.dumper import Dumper, restore
import asyncio
import websockets
import json
import time
import jsonpickle
import time
import sys
from random import randint

admin_tokens=[]
team_tokens=[]

methods_list=[]
admin_methods=["save","print","on_bot_connect", "register_team", "subscribe_leaderboard", "post", "launch_event","remove_edge","remove_node", "stop_game"]

#-=-=-=-=-=-=-=-=-=-=-=-(GAVNO(+-100проц будет переписано))=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

forums=["2ch","4chan","habr"]
currencies_list=["SigmaCoin","Kefirium","DogeCoin","AttendenceCoin"]

class AttendancePrice:
    def __init__(self):
        self.cache_ = [62,61,60,57,51,55,49,56,47,47]
    def __call__(self, x):
        if x < len(self.cache_):
            return self.cache_[x]
        else:
            return self.cache_[-1] - (x-len(self.cache_)) if self.cache_[-1] - (x-len(self.cache_)) > 0 else 1

if len(sys.argv) == 1:
    Model.AcquireLock()
    cur_bases = dict([(c,BaseTrend(100,10,abs(hash(c)))) for c in currencies_list])
    cur_bases["AttendenceCoin"] = AttendancePrice()
    Model.GetInstance()
    Model.GetInstance().market_=Market(30,cur_bases)
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

    Model.GetInstance().graph_=Graph(120,currencies_list)
    vv,ee = GraphGenerator(nteams=nteams,
                    n_outer_ring_vert_per_team=12, 
                    n_core_vert_per_team=6,
                    n_outer_edges=20,
                    n_core_edges=8,
                    n_links=4,
                    seed=0x454a89,
                    debug=True)
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

else:
    restore(sys.argv[1])
    Model.AcquireLock()

Model.GetMarket().Run()
Model.GetGraph().run()
Model.GetWarManager().run()

for name in forums:
    Model.ScheduleRoutine(Routine(Floodilka(name), 30))

time.sleep(2)
Model.ScheduleRoutine(RepeatedRoutine(Dumper("state"),10))
time.sleep(2)
Model.ReleaseLock()
Model.Run()

#restore("state201.save")

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

# async def register_team(websocket, token, team_name):
#     Model.AcquireLock()
#     Model.GetTeams().CreateTeam("TOKEN_"+str(randint(1,100500)),team_name)
#     Model.ReleaseLock()
#     await websocket.send(reply(200,"Team "+team_name+" registered",token))

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
    await websocket.send(reply(200,"OK",token,json.dumps({"name":Model.GetTeams().GetTeam(token).GetName(),"money":[{"name":"dollar","amount":Model.GetTeams().GetTeam(token).GetMoney()}]+[{"name":cur,"amount":Model.GetTeams().GetTeam(token).GetCryptoMoney(cur)} for cur in currencies_list],"nodes":[{"id":node.get_id(),"state":node.get_type(),"power":node.get_power()} for node in Model.GetGraph().get_servers_by_owners(Model.GetTeams().GetTeam(token))],"niggers":Model.GetTeams().GetTeam(token).GetActions()})))

async def upgrade(websocket,token,node_id):
    Model.AcquireLock()
    node_id = int(node_id)
    s = Model.GetGraph().find_server(node_id)
    if Model.GetTeams().GetTeam(token).AddMoneyCheck(-s.get_next_price()) and Model.GetTeams().GetTeam(token).AddActionsCheck(-1):
        Model.GetGraph().upgrade_server(s,s.get_power()*1.5)
        Model.GetTeams().GetTeam(token).AddMoney(-s.get_next_price(), reason="upgrade")
        Model.GetTeams().GetTeam(token).AddActions(-1)
        s.set_next_price(s.get_next_price()*2)
        await websocket.send(reply(200,"OK",token))
    else:
        await websocket.send(reply(228,"Not enough money",token))
    Model.ReleaseLock()

# async def print_team

async def launch_event(websocket, token, event_name):
    Model.AcquireLock()
    ok = True
    try:
        Model.GetEventManager().LoadEvent(event_name)
        Model.GetEventManager().LaunchEvent(event_name)
    except Exception as e:
        print(traceback.format_exc())
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
    #maybe nado v try except obernut', no vrode net
    await websocket.send(reply(200,"OK",token,{"teams":Model.GetTeams().GetTeamsNames(),"forums":forums,"currencies":currencies_list}))
    

async def stop_game(websocket,token):
    Model.AcquireLock()

    for team in Model.GetTeams().GetTeamsList():
        print("!")
        for cur in currencies_list:
            team.RecalculateCryptoToDollar(cur, Model.GetMarket().GetExchangeRate(cur))
        print(team.name_ + " - " + str(team.GetMoney()))

    Model.ReleaseLock()
    await websocket.send(reply(200,"STOPPED",token))

    time.sleep(5)

    Model.AcquireLock()
    # Model.ReleaseLock()
    # ахахаах конец игры - залоченная модель


async def sell(websocket,token,cur,amount):
    amount=float(amount)
    Model.AcquireLock()
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
    Model.GetGraph().del_vertex(Model.GetGraph().find_server(int(node_id)))
    Model.ReleaseLock()
    
    await websocket.send(reply(200,"OK",token))

async def off_node(websocket, token, node_id):
    Model.AcquireLock()
    Model.GetGraph().find_server(int(node_id)).turn_off()
    Model.ReleaseLock()
    
    await websocket.send(reply(200,"OK",token))

async def swap_nodes(websocket, token, node1, node2):
    Model.AcquireLock()
    node1, node2 = int(node1),int(node2)
    serv1 = Model.GetGraph().find_server(node1)
    serv2 = Model.GetGraph().find_server(node2)
    team1 = serv1.get_owner()
    team2 = serv2.get_owner()
    serv1.set_owner(team2)
    serv2.set_owner(team1)
    Model.ReleaseLock()

    await websocket.send(reply(200,"OK",token))


async def buy(websocket,token,cur,amount):
    amount=float(amount)
    Model.AcquireLock();
    if Model.GetTeams().GetTeam(token).AddCryptoMoneyCheck(cur,-amount):
        Model.GetTeams().GetTeam(token).AddMoney(amount/Model.GetMarket().GetExchangeRate(cur))
        Model.GetTeams().GetTeam(token).AddCryptoMoney(cur,-amount,reason="currency exchange")
        Model.ReleaseLock()
        await websocket.send(reply(200,"Crypto exchanged",token))
    else:
        Model.ReleaseLock()
        await websocket.send(reply(228,"Not enough crypto",token))

async def reclassify(websocket, token, node_id, new_state):
    node_id=int(node_id)
    Model.AcquireLock()
    if node_id not in [node.get_id() for node in Model.GetGraph().get_servers_by_owners(Model.GetTeams().GetTeam(token))]:
        # print([node.get_id() for node in Model.GetGraph().get_servers_by_owners(Model.GetTeams().GetTeam(token))])
        Model.ReleaseLock()
        return await websocket.send(reply(208,"not your node",token))

    if not Model.GetTeams().GetTeam(token).AddActionsCheck(-1):
        print(Model.GetTeams().GetTeam(token).GetActions())
        Model.ReleaseLock()
        return await websocket.send(reply(209,"not enough actions",token))
    

    if Model.GetGraph().find_server(node_id).get_type() == "attack":
        Model.GetWarManager().stop_war_by_attacker_id(node_id)

    Model.GetGraph().find_server(node_id).set_type(new_state)
    Model.GetTeams().GetTeam(token).AddActions(-1)
    Model.GetGraph().notify()
    Model.ReleaseLock()

    await websocket.send(reply(200,"OK",token)) 

async def subscribe_leaderboard(websocket, token):
    # def send_leadeboard():
    def teams():
        print("team callback triggered")
        asyncio.run(websocket.send(json.dumps({
            "teams":[{"name":team.GetName(),"color":team.GetColor(),"balance":team.GetMoney()} for team in Model.GetTeams().GetTeamsList()],
            "unitTimer":Model.GetGraph().get_routine().GetRemainingTime()
        })))
    def market():
        print("market callback triggered")
        asyncio.run(websocket.send(json.dumps({"crypto_currencies":[{"name":x,"price":y} for x,y in ((name,Model.GetMarket().GetExchangeRate(name)) for name in currencies_list)]})))

    class teamss(Executable):
        def __init__(self):
            super().__init__()
            self.subs = [None]
        def __call__(self,r):
            print("leaderboard callbakc triggered")
            if websocket.closed and any((sub is not None for sub in self.subs)):
                Model.AcquireLock()
                for sub in self.subs:
                    if sub is not None:
                        Model.EraseSubscription(sub)
                Model.ReleaseLock()
            else:
                Model.AcquireLock()
                try:
                    teams()
                except Exception as e:
                    print(traceback.format_exc())
                    print("exception handled")
                finally:
                    Model.ReleaseLock()
    
    class markett(Executable):
        def __init__(self):
            super().__init__()
            self.sub = None
        def __call__(self,r):
            print("leaderboard callbakc triggered")
            if websocket.closed and self.sub is not None:
                Model.AcquireLock()
                Model.EraseSubscription(self.sub)
                Model.ReleaseLock()
            else:
                Model.AcquireLock()
                market()
                Model.ReleaseLock()
    
    Model.AcquireLock()
    G = teamss()
    G2 = markett()
    S = [Subscription(team,G) for team in Model.GetTeams().GetTeamsList()]
    # S = Subscription(Model.GetTeams(),G)
    S2 = Subscription(Model.GetMarket(),G2)
    G.sub = S
    G2.sub = S2
    [Model.AddSubscription(S1) for S1 in S]
    Model.AddSubscription(S2)
    #====================
    # Model.AcquireLock()
    # [Model.AddSubscription(Subscription(team,teams)) for team in Model.GetTeams().GetTeamsList()]
    # Model.AddSubscription(Subscription(Model.GetMarket(),market))

#=================

    asyncio.create_task(websocket.send(json.dumps({"teams":[{"name":team.GetName(),"color":team.GetColor(),"balance":team.GetMoney()} for team in Model.GetTeams().GetTeamsList()],"unitTimer":Model.GetGraph().get_routine().GetRemainingTime()})))
    
    histories = Model.GetMarket().GetHistories()
    for i in range(len(histories[currencies_list[0]])):
        asyncio.create_task(websocket.send(json.dumps({
            "crypto_currencies":[
                {"name":x,"price":histories[x][i]} for x in currencies_list
            ]})))

    asyncio.create_task(websocket.send(json.dumps({"crypto_currencies":[{"name":x,"price":y} for x,y in ((name,Model.GetMarket().GetExchangeRate(name)) for name in currencies_list)]})))
    Model.ReleaseLock()
    await websocket.send(reply(200,"Succsesfull subscribe",token))

async def subscribe_graph(websocket, token):
    def form_json():
        ret =  json.dumps(
                    {
                        "nodes":[{"id":node.get_id(),"positionX":node.get_x(),"positionY":node.get_y(),"power":node.get_power(),"defense":node.get_power()*node.get_k(),"type":node.get_type(),"level":node.get_level(),"color":node.get_owner().GetColor() if node.get_owner() is not None else None} for node in Model.GetGraph().get_vertexes()],
                        "edges":[{"source":e[0],"target":e[1]} for e in Model.GetGraph().get_edges()],
                        "timers":[{"source":w.get_attacker().get_id(),"target":w.get_defender().get_id(),"timer":Model.GetWarManager().get_war_routine(w).GetRemainingTime()} for w in Model.GetWarManager().get_wars()]
                    })
        return ret


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
                try:
                    asyncio.run(websocket.send(form_json()))
                except Exception as e:
                    print(traceback.format_exc())
                    print("hehehehehe graph execption well handled!!!")
                finally:
                    Model.ReleaseLock()
    
    Model.AcquireLock()
    G = graph()
    G2 = graph()
    S = Subscription(Model.GetGraph(),G)
    S2 = Subscription(Model.GetWarManager(),G2)
    G.sub = S
    G2.sub = S2
    Model.AddSubscription(S)
    Model.AddSubscription(S2)
    Model.ReleaseLock()
    await websocket.send(reply(200,"successfull subscribe",token))

async def subscribe_forum(websocket,token,forum):
    def forum_json():
        return json.dumps({"posts":[{"name":post.GetHeader(),"text":post.GetBody(),"author":post.GetAuthor()} for post in Model.GetNewsFeed().GetPosts(forum)]})

    Model.AcquireLock()
    try:
        asyncio.create_task(websocket.send(forum_json()))
    except Exception as e:
        print(traceback.format_exc())
        print("kto-to obosralsya")
    finally:
        Model.ReleaseLock()
    class forumm(Executable):
        def __init__(self):
            super().__init__()
            self.sub = None
        def __call__(self,r):
            print("foruim callbakc triggered")
            if websocket.closed and self.sub is not None:
                Model.AcquireLock()
                Model.EraseSubscription(self.sub)
                Model.ReleaseLock()
            else:
                Model.AcquireLock()
                try:
                    asyncio.run(websocket.send(forum_json()))
                except Exception as e:
                    print(traceback.format_exc())
                    print("kto-to obosralsya")
                finally:
                    Model.ReleaseLock()
    
    Model.AcquireLock()
    G = forumm()
    # G2 = forum()
    S = Subscription(Model.GetNewsFeed(),G)
    # S2 = Subscription(Model.GetWarManager(),G2)
    G.sub = S
    # G2.sub = S2
    Model.AddSubscription(S)
    # Model.AddSubscription(S2)
    Model.ReleaseLock()
    await websocket.send(reply(200,"successfull subscribe",token))


    # def forumm(r):
    #     print("forum callback triggered")
    #     asyncio.run(websocket.send(json.dumps({"posts":[{"name":post.GetHeader(),"text":post.GetBody(),"author":post.GetAuthor()} for post in Model.GetNewsFeed().GetPosts(forum)]})))
    # Model.AcquireLock()
    # Model.AddSubscription(Subscription(Model.GetNewsFeed(),forumm))
    # Model.ReleaseLock()
    # await websocket.send(reply(200,"successfull subscribe",token))

async def post(websocket,token, forum, author, header, body):
    Model.AcquireLock()
    try:
        Model.GetNewsFeed().SendPost(forum, author, header, body)
        await websocket.send(reply(200,"post posted",token))
    except Exception as e:
        print(traceback.format_exc())
        print("wrong forum")
        await websocket.send(reply(228,"wroung chtiot",token))
    finally:
        Model.ReleaseLock()

async def get_posts(websocket,token,forum):
    await websocket.send(reply(200,"posts acuireseded",token,[{"name":post.GetHeader(),"text":post.GetBody(),"author":post.GetAuthor()} for post in Model.GetNewsFeed().GetPosts(forum)]))

async def attack(websocket,token,id_from,id_to):
    id_from,id_to=int(id_from),int(id_to)
    Model.AcquireLock()
    if id_from not in [node.get_id() for node in Model.GetGraph().get_servers_by_owners(Model.GetTeams().GetTeam(token))]:
        Model.ReleaseLock()
        return await websocket.send(reply(208,"Loh",token))

    if not Model.GetTeams().GetTeam(token).AddActionsCheck(-1):
        print(Model.GetTeams().GetTeam(token).GetActions())
        Model.ReleaseLock()
        return await websocket.send(reply(209,"not enough actions",token))

    if not Model.GetGraph().find_server(id_to) in Model.GetGraph().get_neighbours(Model.GetGraph().find_server(id_from)):
        Model.ReleaseLock()
        return await websocket.send(reply(228,"Нет ребра",token))

    Model.GetWarManager().start_war(Model.GetGraph().find_server(id_from),Model.GetGraph().find_server(id_to))
    Model.GetGraph().find_server(id_from).set_type("attack")
    Model.GetTeams().GetTeam(token).AddActions(-1)

    Model.ReleaseLock()
    await websocket.send(reply(200,"war started!",token))

async def add_edges(websocket, token, id_from, ids_to):
    Model.AcquireLock()
    id_from = int(id_from) 
    node_from = Model.GetGraph().find_server(id_from)
    nodes_to = []
    for id in ids_to:
        nodes_to.append(Model.GetGraph().find_server(int(id)))

    Model.GetGraph().add_edges(node_from, nodes_to) 

    Model.ReleaseLock()

    await websocket.send(reply(200, "Edges added", token))

async def give_node(websocket, token, node_id, team_name):
    Model.AcquireLock()

    team = Model.GetTeams().GetTeamByName(team_name)
    Model.GetGraph().give_server(Model.GetGraph().find_server(int(node_id)), team)

    Model.ReleaseLock()

    await websocket.send(reply(200, "Node given", token))

async def cancel_attack(websocket,token,id_from,id_to):
    id_from,id_to=int(id_from),int(id_to)
    Model.AcquireLock()

    if id_from not in [node.get_id() for node in Model.GetGraph().get_servers_by_owners(Model.GetTeams().GetTeam(token))]:
        Model.ReleaseLock()
        return await websocket.send(reply(208,"Loh",token))

    if not Model.GetTeams().GetTeam(token).AddActionsCheck(-1):
        print(Model.GetTeams().GetTeam(token).GetActions())
        Model.ReleaseLock()
        return await websocket.send(reply(209,"not enough actions",token))

    Model.GetWarManager().stop_war(Model.GetWarManager().get_war(Model.GetGraph().find_server(id_from),Model.GetGraph().find_server(id_to)))

    Model.ReleaseLock()
    await websocket.send(reply(200,"war cancelled!",token))

async def remove_edge(websocket,token,id_from,id_to):
    # await websocket.send(reply(228,"metod ne napisan",token))
    # return
    id_from,id_to=int(id_from),int(id_to)
    Model.AcquireLock()
    Model.GetGraph().del_edges(Model.GetGraph().find_server(id_from),Model.GetGraph().find_server(id_to))
    Model.ReleaseLock()
    await websocket.send(reply(200,"removed_edge",token))

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

        if method in admin_methods and token not in admin_tokens:
            await websocket.send(reply(1337,"method requires admin priviliges",token))
            continue
        
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
