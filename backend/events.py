from backend.model import Model
from backend.wheels.routine import Routine
from backend.wheels.subscriptable import Subscriptable, Subscription, notifier
import threading
import sys

"""
base class for Condition
"""
class Condition:
    def __init__(self):
        self.active_ = False
        self.action_ = None
    def Activate(self, routine):
        self.action_ = routine
        self.active_ = True
    def IsActive(self):
        return self.active_
    def Check(self):
        raise NotImplementedError("Pure virtual method called")
    def GetAction():
        return self.action_
    def Inactivate(self):
        self.active_ = False

"""
example of condition, calculated inplace
"""
class Always (Condition):
    def __init__(self):
        super().__init__()
    def Activate(self, routine):
        super().Activate(routine)
        self.active_ = False
        Model.ScheduleRoutine(routine)
    def Check(self):
        return True

"""
base class for triggered conditions
"""
class TriggeredCondition (Condition):
    def __init__(self, subscriptable):
        super().__init__()
        self.target_ = subscriptable
        self.subscription_ = Subscription(self.target_, self.Watcher_)
    def Activate(self, routine):
        super().Activate(routine)
        Model.AddSubscription(self.subscription_)
    def Watcher_(self, r):
        ret = self.Check()
        if ret:
            self.active_ = False
            Model.EraseSubscription(self.subscription_)
            Model.ScheduleRoutine(self.action_)
    def Inactivate(self):
        super().Inactivate()
        Model.EraseSubscription(self.subscription_)
    def Check(self):
        raise NotImplementedError("Pure virtual method called")

"""
example of triggered condition
"""
class CheckPrice (TriggeredCondition):
    def __init__(self, cur, cond):
        super().__init__(Model.GetMarket())
        self.currency_ = cur
        self.condition_ = cond
    def Check(self):
        Model.AcquireLock()
        ret = self.condition_(Model.GetMarket().GetExchangeRate(self.currency_))
        Model.ReleaseLock()
        return ret

class Coincidence (Condition):
    def __init__(self, conditions_list):
        super().__init__()
        self.conditions_list_ = conditions_list
        self.mutex_ = threading.Lock()
    def Activate(self, routine):
        super().Activate(routine)
        for cond in self.conditions_list_:
            def callback(r):
                self.mutex_.acquire()
                if cond.Check():
                    ret = True
                    for cond2 in self.conditions_list_:
                        if not cond2.IsActive() and not cond2.Check():
                            cond2.Activate(cond2.GetAction)
                            ret = False
                        elif cond2.IsActive():
                            ret = False
                    if ret:
                        self.active_ = False
                        Model.ScheduleRoutine(self.action_)
                self.mutex_.release()
            cond.Activate(Routine(callback))
    def Inactivate(self):
        super().Inactivate()
        for cond in self.conditions_list_:
            cond.Inactivate()
    def Check(self):
        ret = True
        for cond in self.conditions_list_:
            ret = ret and cond.Check()
        return ret
    
class StageCounter (Subscriptable):
    def __init__(self):
        super().__init__()
        self.stage_ = 0
    def GetStage(self):
        return self.stage_
    @notifier
    def SetStage(self, i):
        self.stage_ = i
    @notifier
    def Increment(self):
        self.stage_ += 1

class Stage (TriggeredCondition):
    def __init__(self, stage_counter, cond):
        super().__init__(stage)
        self.stage_counter_ = stage_counter
        self.condition_ = cond
    def Check(self):
        ret = self.condition_(self.stage_counter_.GetStage())
        return ret

class Event:
    def __init__(self,name):
        self.name_ = name
        self.fullname_ = "backend.libevents."+name
        self.eventmodule_ = sys.modules[self.fullname_]
        self.conditions_list_ = []
    def Activate(self):
        self.conditions_list_ = self.eventmodule_.init()
        for cond, routine in self.conditions_list_:
            cond.Activate(routine)
    def Inactivate(self):
        for cond, routine in self.conditions_list_:
            cond.Inactivate()
    def IsActive(self):
        ret = False
        for cond, routine in self.conditions_list_:
            ret = ret or cond.IsActive()
        return ret

class EventManager:
    def __init__(self):
        self.events_ = dict()
    def LoadEvent(self, name):
        ev = Event(name)
        self.events_[name] = ev
    def LaunchEvent(self, name):
        self.events_[name].Activate()
    def StopEvent(self, name):
        self.events_[name].Inactivate()
        
        
        

