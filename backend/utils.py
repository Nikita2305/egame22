class ObjectCounter:
    
    global_sid = 0
        
    def __init__(self):
        self.sid_ = ObjectCounter.global_sid
        ObjectCounter.global_sid += 1

    def IsEqual(self, other):
        return (self.sid_ == other.sid_)        
