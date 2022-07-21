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
        pass #Model.GetGraph().print()


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


tm = TeamsManager([])
Model.GetInstance().graph_ = Graph(1, tm)
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

servers[1].set_type("support")
servers[0].set_type("SSH")

Model.Run()  # Spawns another thread
Model.AcquireLock()
Model.AddSubscription(Subscription(Model.GetGraph(), GraphChangedCallback()))
Model.ScheduleRoutine(Routine(ChangeNameRoutine("g", time.time()), 1))
Model.ReleaseLock()

Model.GetGraph().print()

# TODO: остановка войны раньше её начала
wm =  WarManager(Model.GetGraph().get_vertexes(), 5)
Model.AcquireLock()
wm.start_war(servers[2], servers[3])
Model.ReleaseLock()
w = wm.get_war(servers[2], servers[3])
print("------------------------------------------------")
print(w)

time.sleep(20)
Model.GetGraph().print()
time.sleep(100)
Model.GetTimer().Stop()
