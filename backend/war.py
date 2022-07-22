from backend.model import Model, notifier_with_model_lock
from backend.wheels.routine import Executable, Routine
from backend.server import Server
from backend.wheels.timer import Timer
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.wheels.schedulers import ThreadScheduler
from backend.graph import Graph
import time


class WarManager:
    __wars = {} # {defender: [wars]}
    __war_routines = {} # {war: routine}

    def __init__(self, servers, tick):
        for s in servers:
            self.__wars[s] = []
            self.__tick = tick

    def stop_war(self, war):
        Model.EraseRoutine(self.__war_routines[war])
        self.end_war(war)

    def end_war(self, war):
        self.__wars[war.get_defender()].remove(war)
        del self.__war_routines[war]

    def get_local_wars(self, defender: Server) -> []:
        return self.__wars[defender]
    
    def get_wars(self) -> []:
        ret = []
        for d in self.__wars:
            sum(self.__wars[d],ret)
        return
    
    def get_war_routine(self, war):
        return self.__war_routines[war]

    def get_start_war_shift(self, war):
        local_wars = self.get_local_wars(war.get_defender())
        print(local_wars)
        if [] == local_wars:
            return 0
        latest_war = local_wars[-1]
        #return self.__war_routines[latest_war].GetRemainingTime()
        return 0

    def get_war(self, attacker: Server, defender: Server):
        for war in self.__wars[defender]:
            if war.get_attacker() == attacker:
                return war
        return None

    def shift_local_wars(self, war):
        local_wars = self.get_local_wars(war.get_defender())
        for w in local_wars:
            routine = self.__war_routines[w]
            routine.SetAddTime(self.__tick + routine.GetAddTime())

    def start_war(self, attacker: Server, defender: Server):
        new_war = War(attacker, defender, self)
        self.__wars[defender].append(new_war)
        self.__war_routines[new_war] = Routine(new_war, self.__tick + self.get_start_war_shift(new_war))
        Model.ScheduleRoutine(self.__war_routines[new_war])


class War(Subscriptable, Executable):

    def __init__(self, attacker: Server, defender: Server, manager: WarManager):
        self.__attacker = attacker
        self.__defender = defender
        self.__manager = manager
        super().__init__()

    def get_defender(self) -> Server:
        return self.__defender

    def get_attacker(self) -> Server:
        return self.__attacker

    @notifier_with_model_lock
    def __call__(self, routine: Routine):
        if Model.GetGraph().attack(self.__attacker, self.__defender):
            self.__manager.shift_local_wars(self)
        self.__manager.end_war(self)
