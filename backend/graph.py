from backend.subscriptable import Subscriptable, notifier

class Graph (Subscriptable):
    
    def __init__(self):
        self.name_ = ""
        super().__init__() 
    
    @notifier
    def SetName(self, name):
        self.name_ = name
