import backend.model

class ObjectCounter:
    
    global_sid = 0
        
    def __init__(self):
        self.sid = ObjectCounter.global_sid
        ObjectCounter.global_sid += 1

    def IsEqual(self, other):
        return (self.sid_ == other.sid_)        

class Executable:
    
    def __init__(self):
        pass

    def Execute():
        raise NotImplementedError("Pure virtual method called")

class Routine (ObjectCounter, Executable):
    
    def __init__(self, scheduler):
        self.scheduler_ = scheduler
        super(ObjectCounter).__init__()

    def SafeExecute(self):
        self.Execute()
        backend.model.Model.EraseRoutine(self)

    def Schedule(self):
        self.scheduler_.Schedule(self.SafeExecute)

class Subscription (ObjectCounter):
    
    def __init__(self, subscriptable, executable):
        self.subscriptable_ = subscriptable
        self.executable_ = executable
        super().__init__()

    def IsActive(self):
        return self.subscriptable_.IsMarked()

    def OneShotExecute(self):
        self.subscriptable_.Unmark()
        self.executable_.Execute()

