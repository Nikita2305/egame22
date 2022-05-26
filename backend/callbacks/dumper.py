from backend.model import Model
from backend.routine import Executable
import pickle

class Dumper (Executable):
    
    def __init__(self, filename):
        self.filename_ = filename
        super().__init__()
    
    def __call__(self, routine):
        Model.AcqireLock()
        pickle.dump(Model.GetInstance(), open(self.filename_, "wb"))
        Model.ScheduleRoutine(routine)
        Model.ReleaseLock()
