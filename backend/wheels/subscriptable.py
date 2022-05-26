from functools import wraps
from backend.wheels.utils import ObjectCounter

class Subscriptable:
    
    def __init__(self):
        self.changed_ = False

    def Mark(self):
        self.changed_ = True

    def Unmark(self):
        self.changed_ = False

    def IsMarked(self):
        return self.changed_

def notifier(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        self.Mark()
        return ret
    return wrapper

class Subscription (ObjectCounter):
    
    def __init__(self, subscriptable, executable):
        self.subscriptable_ = subscriptable
        self.executable_ = executable
        super().__init__()

    def IsActive(self):
        return self.subscriptable_.IsMarked()

    def OneShotExecute(self):
        self.subscriptable_.Unmark()
        self.executable_(None)

