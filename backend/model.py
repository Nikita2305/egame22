import threading
from backend.graph import Graph
from backend.market import Market
from backend.newsfeed import NewsFeed
from backend.wheels.subscriptable import Subscription
from backend.wheels.routine import Routine
from backend.wheels.schedulers import ThreadScheduler
from backend.wheels.timer import Timer
from functools import wraps

def singleton(func):
    @wraps(func)
    def wrapper(cls, *args, **kwargs): 
        return func(cls.GetInstance(), *args, **kwargs)
    return wrapper   

class Model:
    """
    - Singleton
    - Любое обращение к методам/полям должно сопровождаться AcquireLock/ReleaseLock
    - Управление Lock-ом полностью на стороне пользователя
    - Корткие критические секции
    """

    instance_ = None
    
    def __init__(self):
        self.graph_ = Graph()
        self.market_ = Market()
        self.news_feed_ = NewsFeed()
        self.mutex_ = threading.Lock()
        self.subscriptions_ = []
        self.routines_ = []
        self.timer_ = Timer()
         
    @classmethod
    def GetInstance(cls):
        if cls.instance_ is None:
            cls.instance_ = Model()
        return cls.instance_

    @classmethod
    @singleton
    def Run(self):
        self.timer_.Run()

    @classmethod
    @singleton
    def GetTimer(self): 
        return self.timer_

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
        try:
            self.subscriptions_.remove(subscription)
            return True
        except ValueError:
            return False

    @classmethod
    @singleton 
    def ScheduleRoutine(self, routine):
        self.routines_.append(routine)
        if routine.IsDeferred():
            routine.ScheduleDefferedExecution() # with Timer
        else:
            routine.Schedule()

    @classmethod
    @singleton 
    def EraseRoutine(self, routine): 
        try:
            self.routines_.remove(routine)
            return True
        except ValueError:
            return False

    @classmethod
    @singleton 
    def AcquireLock(self):
        self.mutex_.acquire()

    @classmethod
    @singleton 
    def ReleaseLock(self, schedule_subscriptions=True): 
        if (schedule_subscriptions):
            self.ScheduleSubscriptions()
        self.mutex_.release()
    
    def ScheduleSubscriptions(self):
        subscriptions_to_execute = []

        for sub in self.subscriptions_:
            if (sub.IsActive()):
                subscriptions_to_execute += [sub]
        for sub in self.subscriptions_:
            sub.InactivateSubject()

        for sub in subscriptions_to_execute:
            sub.GetRoutine().Schedule()

