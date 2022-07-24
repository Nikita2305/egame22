from ast import Mod
from glob import glob
from django.forms import ModelForm
from backend.model import Model
from backend.text_generation.posting import Floodilka
from backend.wheels.routine import Executable, Routine, RepeatedRoutine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.graph import Graph
from backend.server import Server
from backend.market import Market, BaseTrend
from backend.newsfeed import NewsFeed
from backend.teams import Team, TeamsManager
from backend.war import WarManager, War
from backend.wheels.utils import GraphGenerator
from backend.events import EventManager
from backend.callbacks.dumper import Dumper, restore
import asyncio
import websockets
import json
import jsonpickle
import time
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
nteams = 4;
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

Model.ScheduleRoutine(RepeatedRoutine(Dumper("state"),10))

def cb(r):
    print("feeed")
    print(Model.GetNewsFeed().GetPosts("2ch"))

Model.AddSubscription(Subscription(Model.GetNewsFeed(),cb))

time.sleep(2)
Model.Run()

time.sleep(1)
#print("post")
#Model.GetEventManager().LoadEvent("testevent")
#Model.GetEventManager().LaunchEvent("testevent")
restore("state.save")

print(Model.GetNewsFeed().GetPosts("2ch"))

time.sleep(1000)
