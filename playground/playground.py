from backend.model import Model
from backend.routine import Executable, Routine
from backend.subscriptable import Subscription
from backend.schedulers import ThreadScheduler
import time

class GraphChangedCallback (Executable):
    
    def __init__(self): 
        super().__init__()

    def __call__(self, nan):
        print(f"New name: {Model.GetGraph().name_}")


class ChangeNameRoutine (Executable):

    def __init__(self, new_name):
        self.new_name = new_name        
        super().__init__()

    def __call__(self, routine):
        Model.AcquireLock()        
        Model.GetGraph().SetName(self.new_name)
        Model.ReleaseLock() 

# Setup:
Model.Run()
Model.AddSubscription(Subscription(Model.GetGraph(), GraphChangedCallback()))

# Somewhere
Model.ScheduleRoutine(Routine(ThreadScheduler(), ChangeNameRoutine("user defined name"), 1))

