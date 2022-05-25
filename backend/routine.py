import backend.model
from backend.utils import ObjectCounter
import time

class Executable:
    
    def __init__(self):
        pass

    def __call__(self, routine):
        raise NotImplementedError("Pure virtual method called")
        

class Routine (ObjectCounter):
    
    def __init__(self, scheduler, executable, sleeptime=0):
        self.scheduler_ = scheduler 
        self.executable_ = executable
        self.sleeptime_ = sleeptime
        self.execution_started_ = None
        super().__init__()

    def DeferredExecute(self):
        self.execution_started_ = time.time()
        time.sleep(self.sleeptime_)
        self.executable_(self)
        backend.model.Model.EraseRoutine(self) # Erase at most one of several possible equal Routines

    def Schedule(self):
        self.scheduler_.Schedule(self.DeferredExecute)
