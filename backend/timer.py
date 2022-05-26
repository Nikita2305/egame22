import time
import backend.model
from backend.schedulers import ThreadScheduler
from backend.routine import Routine
import threading

class Timer:
    
    def __init__(self, step = 0.1):
        self.routines_ = []
        self.step_ = step
        self.time_ = 0
        self.mutex_ = threading.Lock()

    def GetStep(self):
        return self.step_

    def Run(self):
        self.time_ = time.time()
        backend.model.Model.ScheduleRoutine(Routine(ThreadScheduler(), self.Loop), is_deferred=False) 

    def Loop(self, self_routine):
        time.sleep(self.step_)
        self.time_ += self.step_
        ex_routines = []
        new_routines = []

        self.mutex_.acquire()
        for routine, add_time in self.routines_:
            if (self.time_ - add_time >= routine.GetSleepTime()):
                ex_routines += [routine]
            else:
                new_routines += [(routine, add_time)]
        self.routines_ = new_routines 
        self.mutex_.release()

        for routine in ex_routines:
            routine.Schedule()

        backend.model.Model.ScheduleRoutine(self_routine, is_deferred=False)
            
    def Add(self, routine):
        self.mutex_.acquire()
        self.routines_ += [(routine, self.time_)]
        self.mutex_.release()
