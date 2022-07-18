import backend.model
from backend.wheels.utils import ObjectCounter
from backend.wheels.schedulers import ThreadScheduler
import time
import threading

class Executable:
    
    def __init__(self):
        pass

    def __call__(self, routine):
        raise NotImplementedError("Pure virtual method called")
        

class Routine:
    
    def __init__(self, executable, sleeptime=None):
        self.scheduler_ = ThreadScheduler()
        self.executable_ = executable
        self.sleeptime_ = sleeptime
        self.addtime_ = None
        self.mutex_ = threading.Lock()
        self.execution_started_ = None
        self.executed_ = False
        super().__init__()

    def GetSleepTime(self):
        return self.sleeptime_
    
    def GetAddTime(self):
        return self.addtime_
    
    def SetAddTime(self, t):
        self.addtime_ = t
        
    def IsExecuted():
        return self.executed_

    def GetRemainingTime(self):
        if self.addtime_ is None or self.sleeptime_ is None:
            return None
        now = backend.model.Model.GetTimer().GetTime()
        return self.sleeptime_ - (now - self.addtime_)

    def Execute(self): 
        self.mutex_.acquire()
        self.executable_(self)
        self.executed_ = True;
        self.mutex_.release()
        backend.model.Model.AcquireLock()
        backend.model.Model.EraseRoutine(self) # Erase at most one of several possible equal Routines
        backend.model.Model.ReleaseLock(schedule_subscriptions=False)

    def Schedule(self):
        self.executed_ = False;
        self.scheduler_.Schedule(self.Execute)
   
    def IsDeferred(self):
        return self.sleeptime_ is not None
 
    def ScheduleDefferedExecution(self):
        self.executed = False;
        backend.model.Model.GetTimer().Add(self)
