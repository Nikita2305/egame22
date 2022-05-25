from backend.subscription import Routine
import time
import pickle

class Scheduler:

    def Schedule(self, executable):
        executable.Execute()

class Dumper (Routine):
    
    def __init__(self, filename):
        self.filename_ = filename
        super().__init__(Scheduler)

    def Execute(self):
        while (True):
            time.sleep(10)
            Model.AcqireLock()
            pickle.dump(Model.GetInstance(), open(filename, "wb"))
            Model.ReleaseLock()
