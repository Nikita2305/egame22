from backend.model import Model
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription
from backend.wheels.schedulers import ThreadScheduler
import time

class GraphChangedCallback (Executable):
    
    def __init__(self): 
        super().__init__()

    def __call__(self, nan):
        print(f"New name: {Model.GetGraph().name_}")


class ChangeNameRoutine (Executable):

    def __init__(self, new_name, time):
        self.new_name = new_name
        self.time = time   
        super().__init__()

    def __call__(self, routine):
        Model.AcquireLock()        
        Model.GetGraph().SetName(self.new_name)
        print("Expected 1s: ", time.time() - self.time)
        Model.ReleaseLock() 

# Setup:
Model.Run() # Spawns another thread
Model.AddSubscription(Subscription(Model.GetGraph(), GraphChangedCallback()))

# Somewhere
Model.ScheduleRoutine(Routine(ChangeNameRoutine("user defined name", time.time()), 1))
print("wait for it")

time.sleep(2)
print("wait for it")

time.sleep(2)
print("bye")
Model.GetTimer().Stop()
