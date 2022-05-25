from functools import wraps

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
