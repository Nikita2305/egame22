import time
import backend.model
from backend.wheels.schedulers import ThreadScheduler
from backend.wheels.routine import Routine
import threading

class Timer:
    
    def __init__(self, step = 0.1):
        self.routines_ = []
        self.step_ = step
        self.time_ = 0
        self.stopped_ = False
        self.mutex_ = threading.Lock()

    def GetTime(self):
        return self.time_

    def Run(self):
        backend.model.Model.AcquireLock()
        backend.model.Model.ScheduleRoutine(Routine(self.Loop))
        backend.model.Model.ReleaseLock(schedule_subscriptions=False)

    def Stop(self):
        self.mutex_.acquire()
        self.stopped_ = True
        self.mutex_.release()

    def Loop(self, self_routine):
        time.sleep(self.step_)
        backend.model.Model.AcquireLock()
        self.mutex_.acquire() 
        self.time_ += self.step_
        backend.model.Model.ScheduleRoutine(Routine(self.ScheduleExpired))
        if not self.stopped_:
            backend.model.Model.ScheduleRoutine(self_routine)
        self.mutex_.release()
        backend.model.Model.ReleaseLock(schedule_subscriptions=False)
            
    def ScheduleExpired(self, self_routine):
        #new_routines = []
        self.mutex_.acquire()
        for routine in self.routines_:
            if routine.GetRemainingTime() <= 0:
                routine.Schedule()
            #else:
                #new_routines.append(routine)
        #self.routines_ = new_routines 
        self.mutex_.release()        

    def Add(self, routine):
        #print("timer.add 1")
        self.mutex_.acquire()
        #print("timer.add 2")
        routine.SetAddTime(self.time_)
        self.routines_.append(routine)
        self.mutex_.release()

    def Remove(self, routine):
        self.mutex_.acquire()
        try:
            self.routines_.remove(routine)
            self.mutex_.release()
            return True
        except ValueError:
            self.mutex_.release()
            return False
