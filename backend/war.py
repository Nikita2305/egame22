from backend.model import Model, notifier_with_model_lock
from backend.wheels.routine import Executable, Routine
from backend.server import Server
from backend.wheels.timer import Timer
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.wheels.schedulers import ThreadScheduler
from backend.graph import Graph
import time
import threading

class WarManager(Subscriptable):

    def __init__(self, servers, tick):
        super().__init__()
        self.__wars = {} # {defender: [wars]}
        self.__war_routines = {} # {war: routine}
        self.__war_remaining_time = {}
        for s in servers:
            self.__wars[s] = []
            self.__tick = tick
    
    def run(self):
        for w in self.__war_remaining_time:
            self.__war_routines[w] = Routine(w, self.__war_remaining_time[w])
            Model.ScheduleRoutine(self.__war_routines[w])
    
    def __getstate__(self):
        self.__war_remaining_time = dict([(w,self.__war_routines[w].GetRemainingTime()) for w in self.__war_routines])
        state = self.__dict__.copy()
        del state["mutex_"]
        del state["changed_"]
        del state["_WarManager__war_routines"]
        return state
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.changed_ = False
        self.mutex_ = threading.Lock()
        self.__war_routines = {}

    @notifier
    def stop_war(self, war):
        Model.EraseRoutine(self.__war_routines[war])
        self.end_war(war)

    # бесполезная
    @notifier
    def end_war(self, war):
        self.__wars[war.get_defender()].remove(war)
        del self.__war_routines[war]

    def get_local_wars(self, defender: Server) -> []:
        return self.__wars[defender]
    
    def get_wars(self) -> []:
        ret = []
        for d in self.__wars.keys():
            ret += self.__wars[d]
        print(ret)
        return ret
    
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

    def stop_war_by_attacker_id(self, attacker_id):
        attacker = Model.GetGraph().find_server(attacker_id)
        for defender in Model.GetGraph().get_vertexes():
            war = Model.GetWarManager().get_war(attacker, defender)
            if war != None:
                Model.GetWarManager().stop_war(war)

    @notifier
    def shift_local_wars(self, war):
        local_wars = self.get_local_wars(war.get_defender())
        for w in local_wars:
            routine = self.__war_routines[w]
            routine.SetAddTime(self.__tick + routine.GetAddTime())

    @notifier
    def start_war(self, attacker: Server, defender: Server):
        new_war = War(attacker, defender, self)
        self.__wars[defender].append(new_war)
        self.__war_routines[new_war] = Routine(new_war, self.__tick + self.get_start_war_shift(new_war))
        Model.ScheduleRoutine(self.__war_routines[new_war])


class War(Executable):

    def __init__(self, attacker: Server, defender: Server, manager: WarManager):
        self.__attacker = attacker
        self.__defender = defender
        self.__manager = manager
        super().__init__()

    def get_defender(self) -> Server:
        return self.__defender

    def get_attacker(self) -> Server:
        return self.__attacker

    def __call__(self, routine: Routine):
        Model.AcquireLock()
        if Model.GetGraph().attack(self.__attacker, self.__defender):
            self.__manager.shift_local_wars(self)
        self.__manager.end_war(self)
        Model.ReleaseLock()
        
    def __str__(self):
        return str("War: ")+str(self.__attacker)+" attacks "+str(self.__defender)
