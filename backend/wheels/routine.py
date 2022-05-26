import backend.model
from backend.wheels.utils import ObjectCounter
from backend.wheels.schedulers import ThreadScheduler
import time

class Executable:
    
    def __init__(self):
        pass

    def __call__(self, routine):
        raise NotImplementedError("Pure virtual method called")
        

class Routine (ObjectCounter):
    
    def __init__(self, executable, sleeptime=0):
        self.scheduler_ = ThreadScheduler()
        self.executable_ = executable
        self.sleeptime_ = sleeptime
        self.execution_started_ = None
        super().__init__()

    def GetSleepTime(self):
        return self.sleeptime_

    def Execute(self): 
        self.executable_(self)
        backend.model.Model.AcquireLock()
        backend.model.Model.EraseRoutine_(self) # Erase at most one of several possible equal Routines
        backend.model.Model.ReleaseLock(schedule_subscriptions=False)

    def Schedule(self):
        self.scheduler_.Schedule(self.Execute)
    
    def ScheduleDefferedExecution(self):
        backend.model.Model.GetTimer().Add(self)
