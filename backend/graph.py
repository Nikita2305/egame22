import time

from backend.wheels.subscriptable import Subscriptable, notifier
from backend.wheels.routine import Executable, Routine
from backend.model import Model, notifier_with_model_lock
from backend.vertex import Vertex
from backend.teams import Team
from backend.server import Server


class Graph(Subscriptable, Executable):
    __graph = {}

    def __init__(self, tick, teams_manager):
        self.__teams_manager = teams_manager
        self.__tick = tick
        super().__init__()
        Model.ScheduleRoutine(Routine(self, self.__tick))

    @notifier
    def __call__(self, routine):
        # TODO: нужно ли обнулять action, get for teammanager
        '''for token in self.__teams_manager.teams_.keys():
            team = self.__teams_manager.GetTeam(token)
            team.AddActions(-(team.GetActions()))'''
        vertexes = self.get_vertexes()
        for v in vertexes:
            if v.get_owner() is None:
                continue
            v.get_owner().AddActions(v.get_moves())
            #v.get_owner().AddCryptoMoney(v.get_crypto_money())
        print("AHAHA")
        for k in self.__teams_manager.teams_.keys():
            print(self.__teams_manager.GetTeam(k).actions_)
        print(time.time())
        Model.ScheduleRoutine(routine)

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

    def get_servers_by_owners(self, owner: Team) -> []:
        servers = []
        for v in self.__graph.keys():
            if v.get_owner() == owner:
                servers.append(v)
        return servers

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

    def print(self):
        print(self)
        for s in self.__graph.keys():
            s.print("    ")
