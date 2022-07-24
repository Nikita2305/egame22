import time

from backend.wheels.subscriptable import Subscriptable, notifier
from backend.wheels.routine import Executable, Routine
from backend.model import Model, notifier_with_model_lock
from backend.vertex import Vertex
from backend.teams import Team
from backend.server import Server
import threading

class Graph(Subscriptable, Executable):

    def __init__(self, tick, currencies_bases_dict):
        super().__init__()
        self.__graph = {}
        self.__curr = currencies_bases_dict
        self.__tick = tick
        self.__routine = Routine(self, self.__tick)

    def run(self):
        Model.ScheduleRoutine(self.__routine)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_Graph__routine"]
        del state["mutex_"]
        del state["changed_"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__routine = Routine(self, self.__tick)
        self.changed_ = False
        self.mutex_ = threading.Lock()

    @notifier_with_model_lock
    def __call__(self, routine):
        new_resources = {} # {team: {"actions":, "BTC": ,...}}
        teams = Model.GetTeams().GetTeamsList()
        for t in teams:
            new_resources[t] = {}
            new_resources[t]["actions"] = 0
            for c in self.__curr:
                new_resources[t][c] = 0
        vertexes = self.get_vertexes()
        for v in vertexes:
            if v.get_owner() is None:
                continue
            new_resources[v.get_owner()]["actions"] += v.get_moves()
            if v.get_type() in self.__curr:
                new_resources[v.get_owner()][v.get_type()] += v.get_crypto_money()

        for t in teams:
            t.SetActions(new_resources[t]["actions"]+4,reason="restore") #reset actions, 4 -- default without ssh 
            for c in self.__curr:
                t.AddCryptoMoney(c, new_resources[t][c], "mining")

        print("AHAHA")
        for k in Model.GetTeams().teams_.keys():
            print(Model.GetTeams().GetTeam(k).actions_)
            print(Model.GetTeams().GetTeam(k).cryptowallet_)
        print(time.time())
        Model.ScheduleRoutine(routine)

    def get_curr(self):
        return self.__curr

    def find_same_vertex(self, vertex: Vertex):
        for v in self.__graph.keys():
            if id(v) == id(vertex):
                return vertex
        return -1

    @notifier
    def init_vertex(self, vertex):
        if self.find_same_vertex(vertex) == -1:
            self.__graph[vertex] = []

    @notifier
    def add_edges(self, vertex: Vertex, vertexes_edges: []):
        self.init_vertex(vertex)
        for v in vertexes_edges:
            self.init_vertex(v)
            # TODO: rewrite without checking
            if self.__graph[self.find_same_vertex(vertex)].count(self.find_same_vertex(v)) == 0:
                self.__graph[self.find_same_vertex(vertex)].append(self.find_same_vertex(v))
                self.__graph[self.find_same_vertex(v)].append(self.find_same_vertex(vertex))

    @notifier
    def del_edges(self, vertex1: Vertex, vertex2: Vertex):
        vertex1 = self.find_same_vertex(vertex1)
        vertex2 = self.find_same_vertex(vertex2)
        self.__graph[vertex1].remove(vertex2)
        self.__graph[vertex2].remove(vertex1)

    @notifier
    def del_vertex(self, vertex: Vertex):
        vertex = self.find_same_vertex(vertex)
        for v in self.__graph[vertex]:
            self.del_edges(v, vertex)
        del self.__graph[vertex]

    def get_neighbours(self, vertex: Vertex) -> []:
        if self.find_same_vertex(vertex) == -1:
            return -1
        return self.__graph[self.find_same_vertex(vertex)]

    def get_vertexes(self) -> []:
        return list(self.__graph.keys())

    def get_edges(self) -> []:
        ret = []
        lst = self.get_vertexes()
        for i in range(len(lst)):
            for j in range(i+1,len(lst)):
                v0 = lst[i]
                v1 = lst[j]
                if v1 in self.__graph[v0]:
                    ret.append((v0.get_id(),v1.get_id()))
        return ret

    def get_servers_by_owners(self, owner: Team) -> []:
        servers = []
        for v in self.__graph.keys():
            if v.get_owner() == owner:
                servers.append(v)
        return servers

    @notifier
    def notify(self):
        pass

    def find_server(self, id):
        for v in self.__graph.keys():
            if v.get_id() == id:
                return v
        return None

    def get_moves(self, owner: Team):
        moves = 0
        owner_servers = self.get_servers_by_owners(owner)
        for server in owner_servers:
            moves += server.get_moves()
        return moves

    @notifier
    def upgrade_server(self, server: Server, new_power):
        server.set_power(new_power)

    @staticmethod
    def get_server_type(self, server: Server):
        return server.get_type()

    @notifier
    def set_server_type(self, server: Server, new_type: str):
        server.set_type(new_type)

    def get_sum_power_server(self, server: Server):
        gift_power = 0
        friends = set(self.get_servers_by_owners(server.get_owner()))
        for s in set(self.get_neighbours(server)):
            if s in friends and s.get_type() == "support":
                gift_power += s.get_power_gift()
        return gift_power + server.get_power()

    @notifier
    def attack(self, attacking_server: Server, defending_server: Server):
        if attacking_server.get_type() != "attack":
            attacking_server.set_type("attack")
        if not (self.get_sum_power_server(attacking_server) >= self.get_sum_power_server(defending_server) * defending_server.get_k()) or not(defending_server in self.get_neighbours(attacking_server)) or not(attacking_server.is_enabled()) or not(defending_server.is_enabled()):
            return 0
        defending_server.set_owner(attacking_server.get_owner())
        return 1
    
    def get_routine(self):
        return self.__routine

    def print(self):
        print(self)
        for s in self.__graph.keys():
            s.print("    ")
