from functools import wraps
from backend.wheels.routine import Routine
import threading

class Subscriptable:
    
    def __init__(self):
        self.changed_ = False
        self.mutex_ = threading.Lock()
    
    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if self.mutex_.locked():
            self.mutex_.release()

    def Mark(self):
        self.mutex_.acquire()
        self.changed_ = True
        self.mutex_.release()

    def Unmark(self):
        self.mutex_.acquire()
        self.changed_ = False
        self.mutex_.release()

    def IsMarked(self):
        self.mutex_.acquire()
        is_changed = self.changed_
        self.mutex_.release()
        return is_changed

def notifier(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        self.Mark()
        return ret
    return wrapper

class Subscription:
    
    def __init__(self, subscriptable, executable):
        self.subscriptable_ = subscriptable
        self.routine_ = Routine(executable)
        super().__init__()

    def InactivateSubject(self):
        self.subscriptable_.Unmark()

    def IsActive(self):
        try:
            return self.subscriptable_.IsMarked() 
        except Exception as e:
            print(self,"and",self.subscriptable_)
            raise e

    def GetRoutine(self):
        return self.routine_
