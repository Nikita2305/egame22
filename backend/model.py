import threading
from backend.graph import Graph
from backend.market import Market
from backend.newsfeed import NewsFeed
from backend.subscriptable import Subscription
from backend.routine import Routine
from backend.schedulers import ThreadScheduler
from functools import wraps

def singleton(func):
    @wraps(func)
    def wrapper(cls, *args, **kwargs): 
        return func(cls.GetInstance(), *args, **kwargs)
    return wrapper   

class Model:

    instance_ = None
    
    def __init__(self):
        self.graph_ = Graph()
        self.market_ = Market()
        self.news_feed_ = NewsFeed()
        self.mutex_ = threading.Lock()
        self.subscriptions_ = []
        self.routines_ = []

    @classmethod
    def GetInstance(cls):
        if cls.instance_ is None:
            cls.instance_ = Model()
        return cls.instance_

    @classmethod
    @singleton 
    def GetGraph(self):
        return self.graph_

    @classmethod
    @singleton 
    def GetMarket(self):
        return self.market_

    @classmethod
    @singleton 
    def GetNewsFeed(self): 
        return self.news_feed_ 

    @classmethod
    @singleton 
    def AddSubscription(self, subscription):
        self.subscriptions_.append(subscription)

    @classmethod
    @singleton 
    def EraseSubscription(self, subscription):
        for i, s in enumerate(self.subscriptions_):
            if (s.IsEqual(subscription)):
                self.subscriptions_.pop(i)
                return True
        return False

    @classmethod
    @singleton 
    def ScheduleRoutine(self, routine):
        self.routines_.append(routine)
        routine.Schedule()

    @classmethod
    @singleton 
    def EraseRoutine(self, routine):
        for i, s in enumerate(self.routines_):
            if (s.IsEqual(routine)):
                self.routines_.pop(i)
                return True
        return False

    @classmethod
    @singleton 
    def AcquireLock(self):
        self.mutex_.acquire()

    @classmethod
    @singleton 
    def ReleaseLock(self): 
        self.ScheduleRoutine(Routine(ThreadScheduler(), self.ExecuteSubscriptions_))
        self.mutex_.release() 

    def ExecuteSubscriptions_(self, nan):
        while (self.ExecuteSingleSubscription_()):
            pass
    
    def ExecuteSingleSubscription_(self):
        for subscription in self.subscriptions_:
            if (subscription.IsActive()):
                subscription.OneShotExecute()
                return True
        return False
