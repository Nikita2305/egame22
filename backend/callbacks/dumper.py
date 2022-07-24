from backend.model import Model
from backend.wheels.routine import Executable
import jsonpickle
import threading
import jsonpickle.ext.numpy as jsonpickle_numpy

jsonpickle_numpy.register_handlers()

class MutexHandler (jsonpickle.handlers.BaseHandler):
    def flatten(obj, data):
        pass
    def restore(obj):
        return threading.Lock()

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
        s = jsonpickle.encode(Model.GetInstance(),
                              make_refs=True, 
                              keys=True, 
                              warn=True)
        Model.ReleaseLock()
        f = open(self.filename_+str(int(tm))+".save", "w", encoding="utf-8")
        f.write(s)
        f.close()
        print("Saved")
        
def restore(filename):
    with open(filename, encoding="utf-8") as f:
        read_data = f.read()
        m = jsonpickle.decode(read_data)
        Model.instance_ = m
        f.close()
        
        
