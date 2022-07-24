from locale import currency
from backend.wheels.subscriptable import Subscriptable, notifier
from backend.model import Model, notifier_with_model_lock
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
import time
import traceback
import math
import copy
import threading

import numpy as np

class BumpSpline:
    def __init__(self, x1, y1, x2, y2, x3, y3):
        self.x1_ = x1
        self.x2_ = x2
        self.x3_ = x3
        self.y1_ = y1
        self.y2_ = y2
        self.y3_ = y3
        a = np.array([[x1**3, x1**2, x1, 1],
                      [x2**3, x2**2, x2, 1],
                      [3*x1**2, 2*x1, 1, 0],
                      [3*x2**2, 2*x2, 1, 0]])
        b = np.array([y1,y2,0,0])
        x = np.linalg.solve(a, b)
        self.par1_ = list(x)
        a = np.array([[x2**3, x2**2, x2, 1],
                      [x3**3, x3**2, x3, 1],
                      [3*x2**2, 2*x2, 1, 0],
                      [3*x3**2, 2*x3, 1, 0]])
        b = np.array([y2,y3,0,0])
        x = np.linalg.solve(a, b)
        self.par2_ = list(x)
    
    def _calculate(self, x, par):
        return par[0]*x**3+par[1]*x**2+par[2]*x+par[3]
    
    def __call__(self, x):
        if self.x3_ < x:
            return self.y3_
        elif self.x2_ < x:
            return self._calculate(x,self.par2_)
        elif self.x1_ < x:
            return self._calculate(x,self.par1_)
        else:
            return self.y1_
        
    def expired(self, x):
        return x > self.x3_

def call_or_check(f,x):
    try:
        return f.expired(x)
    except AttributeError:
        return False

class SingleMarket:
    def __init__(self, base_trend):
        self.functions_list_ = [base_trend]
        self.history_ = [self.Calculate(0)]
    
    def Calculate(self, time):
        res = 1.
        for f in self.functions_list_:
            res *= f(time)
        return res
            
    def Tick(self, time):
        self.history_.append(self.Calculate(time))
        self.functions_list_ = [f for f in self.functions_list_ if not call_or_check(f,time)]
        
    def GetExchangeRate(self):
        return self.history_[-1]
    
    def GetHistory(self):
        return self.history_
    
    def GetPredict(self, end_time):
        ret = copy.copy(self.history_)
        time = len(self.history_)
        for t in range(time,end_time):
            ret.append(self.Calculate(t))
        return ret
    
    def AddFunction(self, f):
        self.functions_list_.append(f)

class Market (Subscriptable, Executable):

    def __init__(self, tick, currencies_bases_dict):
        super().__init__()
        self.tick_time_ = tick
        self.markets_ = dict()
        for cur in currencies_bases_dict:
            self.markets_[cur] = SingleMarket(currencies_bases_dict[cur])
        self.time_ = 0
        self.time_converter_ = [Model.GetTimer().GetTime()]
        
    def Run(self):
        Model.ScheduleRoutine(Routine(self, self.tick_time_))
        
    def __getstate__(self):
        state = self.__dict__.copy()
        del state["mutex_"]
        del state["changed_"]
        return state
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.changed_ = False
        self.mutex_ = threading.Lock()
    
    @notifier_with_model_lock
    def __call__(self, routine):
        self.time_ += 1
        self.time_converter_.append(Model.GetTimer().GetTime())
        for cur in self.markets_:
            self.markets_[cur].Tick(self.time_)
        Model.ScheduleRoutine(routine)
    
    @notifier
    def AddFunction(self, cur, f):
        self.markets_[cur].AddFunction(f);
    
    def GetPredict(self, cur, end_time):
        return self.markets_[cur].GetPredict(end_time);
        
    def GetHistory(self, cur):
        return self.markets_[cur].GetHistory();

    def GetHistories(self):
        histories = {}
        for cur in self.markets_.keys():
            histories[cur] = self.GetHistory(cur)

        return histories
    
    def GetExchangeRate(self, cur):
        return self.markets_[cur].GetExchangeRate();
        
    def AddBump(self, cur, start, peak, end, amplitude):
        f = BumpSpline(self.time_+start, 1., self.time_+peak, amplitude, self.time_+end, 1.)
        self.AddFunction(cur, f)
        
    def ConvertTime(self, time):
        if time < len(self.time_converter_):
            return self.time_converter_[time]
        else:
            return self.time_converter_[-1]+(time - self.time_)*self.tick_time_

class BaseTrend:
    def __init__(self,start,sigma, seed=12345):
        self.start_ = start
        self.sigma_ = sigma
        self.cache_ = [start]
        self.rng_ = np.random.default_rng(seed)
    
    def Drift(self, x):
        return x + self.rng_.normal(0,self.sigma_)
    
    def __call__(self, x):
        if x >= len(self.cache_):
            for t in range(len(self.cache_),x+1):
                self.cache_.append(self.Drift(self.cache_[t-1]))
                while self.cache_[t] <= 0:
                    self.cache_[t] = self.Drift(self.cache_[t-1])
        return self.cache_[x]
