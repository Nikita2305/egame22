from backend.model import Model
from backend.wheels.routine import Executable
import pickle
import threading
#import pickle.ext.numpy as pickle_numpy

#jsonpickle_numpy.register_handlers()

class Dumper (Executable):
    """
    Потенциально устарело
    """
    
    def __init__(self, filename):
        self.filename_ = filename
        super().__init__()
        #jsonpickle.handlers.register(threading.Lock,MutexHandler)
    
    def __call__(self, routine):
        Model.AcquireLock()
        tm = Model.GetTimer().GetTime()
        print("Saving to",self.filename_+str(int(tm))+".save")
        with open(self.filename_+str(int(tm))+".save", 'wb') as f:
            pickle.dump(Model.instance_, f, pickle.HIGHEST_PROTOCOL)
            f.close()
        Model.ReleaseLock()
        print("Saved")
        
def restore(filename):
    with open(filename, 'rb') as f:
        Model.instance_ = pickle.load(f)
        f.close()
        
        
