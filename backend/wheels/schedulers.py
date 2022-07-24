from threading import Thread

class Scheduler:
    
    def Schedule(self, executable):
        raise NotImplementedError("pure virtual method called")

class InplaceScheduler (Scheduler):

    def Schedule(self, executable):
        executable()

class ThreadScheduler (Scheduler):
    
    def Schedule(self, executable):
        T = Thread(target=executable)
        T.start()
        
