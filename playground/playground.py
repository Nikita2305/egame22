from backend.model import Model
from backend.wheels.routine import Executable, Routine, RepeatedRoutine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.wheels.schedulers import ThreadScheduler
from backend.graph import Graph
from backend.market import Market
from backend.server import Server
from backend.teams import Team, TeamsManager
from backend.war import WarManager, War
from backend.wheels.utils import GraphGenerator
from backend.newsfeed import NewsFeed
import time
from backend.text_generation.posting import Floodilka

"""colors = [
    "#4281A4",
    "#080357",
    "#FF6B6B",
    "#F8F4A6",
    "#BDF7B7",
    "#37DB25",
    "#F1A6F7",
    "#1D1D1D"
    ]

class GraphChangedCallback(Executable):

    def __init__(self):
        super().__init__()

    def __call__(self, routine):
        print("graph changed")#Model.GetGraph().print()


class ChangeNameRoutine(Executable):

    def __init__(self, new_name, time):
        self.new_name = new_name
        self.time = time
        super().__init__()

    def __call__(self, routine):
        Model.AcquireLock()
        print("Expected 1s: ", time.time() - self.time)
        Model.ReleaseLock()

    # Setup:

Model.GetInstance()
tm = TeamsManager(["BTC", "EPH", "RUB"])
Model.GetInstance().graph_ = Graph(1, tm, ["BTC", "EPH", "RUB"])
servers = []

gr = GraphGenerator(nteams=5, 
                   n_outer_ring_vert_per_team=12, 
                   n_core_vert_per_team=6,
                   n_outer_edges=16,
                   n_core_edges=8,
                   n_links=4)

for v in gr[0]:
    s = Server(Model.GetGraph(), v.i)
    s.set_x(v.x)
    s.set_y(v.y)
    s.set_power(v.power)
    servers.append(s)

for e in gr[1]:
    Model.GetGraph().add_edges(servers[e[0].i], [servers[e[1].i]])

tm.CreateTeam(1, "A", "")
tm.CreateTeam(2, "B")

print(tm.GetTeamsNames())

servers[0].set_owner(tm.GetTeam(1))
servers[1].set_owner(tm.GetTeam(1))
servers[2].set_owner(tm.GetTeam(1))
servers[3].set_owner(tm.GetTeam(2))
servers[4].set_owner(tm.GetTeam(2))

servers[1].set_type("BTC")
servers[0].set_type("BTC")


Model.Run()  # Spawns another thread
Model.AcquireLock()
Model.AddSubscription(Subscription(Model.GetGraph(), GraphChangedCallback()))
Model.ScheduleRoutine(Routine(ChangeNameRoutine("g", time.time()), 1))
Model.ReleaseLock()

time.sleep(5)
for k in tm.teams_.keys():
    print(tm.GetTeam(k).actions_)
    print(tm.GetTeam(k).cryptowallet_)
"""

def callback(routine):
    print("changed!!")

def cb2(routine):
    Model.AcquireLock()
    Model.GetNewsFeed().SendPost("2ch","aaa","aaa","aaa")
    Model.ScheduleRoutine(routine)
    Model.ReleaseLock()
    
    print("tick")
Model.GetInstance()
Model.GetInstance().news_feed_ = NewsFeed(["2ch", "4chan", "habr"])
Model.Run()  # Spawns another thread
Model.AcquireLock()
Model.AddSubscription(Subscription(Model.GetNewsFeed(), callback))
#Model.ScheduleRoutine(Routine(cb2,1))
r = Routine(Floodilka("2ch"), 1)
r.debug_flag = 1
Model.ScheduleRoutine(r)
# Model.ScheduleRoutine(Routine(Floodilka("habr"), 1))
Model.ReleaseLock()
print("end init")
time.sleep(100)

'''
from backend.model import Model
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.wheels.schedulers import ThreadScheduler
from backend.graph import Graph
from backend.server import Server
from backend.teams import Team, TeamsManager
from backend.war import WarManager, War
import time


class GraphChangedCallback(Executable):

    def __init__(self):
        super().__init__()

    def __call__(self, routine):
        Model.GetGraph().print()


class ChangeNameRoutine(Executable):

    def __init__(self, new_name, time):
        self.new_name = new_name
        self.time = time
        super().__init__()

    def __call__(self, routine):
        Model.AcquireLock()
        print("Expected 1s: ", time.time() - self.time)
        Model.ReleaseLock()

    # Setup:


tm = TeamsManager(["BTC", "EPH", "RUB"])
Model.GetInstance().graph_ = Graph(1, tm, ["BTC", "EPH", "RUB"])
servers = []
for i in range(5):
    servers.append(Server(Model.GetGraph(), i + 1000))

for i in range(5):
    servers.append(Server(Model.GetGraph(), i + 1000))
    Model.GetGraph().add_edges(servers[i], [servers[(i+1) % 5]])

tm.CreateTeam(1, "A")
tm.CreateTeam(2, "B")

servers[0].set_owner(tm.GetTeam(1))
servers[1].set_owner(tm.GetTeam(1))
servers[2].set_owner(tm.GetTeam(1))
servers[3].set_owner(tm.GetTeam(2))
servers[4].set_owner(tm.GetTeam(2))

servers[1].set_type("BTC")
servers[0].set_type("SSH")

Model.Run()  # Spawns another thread
Model.AcquireLock()
Model.AddSubscription(Subscription(Model.GetGraph(), GraphChangedCallback()))
Model.ScheduleRoutine(Routine(ChangeNameRoutine("g", time.time()), 1))
Model.ReleaseLock()
w = wm.get_war(servers[2], servers[3])
print("------------------------------------------------")
print(w)
Model.AcquireLock()
wm.stop_war(w)
Model.ReleaseLock()'''
