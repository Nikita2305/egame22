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

    def Run(self):
        self.time_ = time.time()
        backend.model.Model.AcquireLock()
        backend.model.Model.ScheduleRoutine(Routine(self.Loop))
        backend.model.Model.ReleaseLock(schedule_subscriptions=False)

    def Stop(self):
        self.mutex_.acquire()
        self.stopped_ = True
        self.mutex_.release()

    def Loop(self, self_routine):
        time.sleep(self.step_)
        self.time_ += self.step_

        self.mutex_.acquire() 
        backend.model.Model.AcquireLock()
        backend.model.Model.ScheduleRoutine(Routine(self.ScheduleExpired))
        if not self.stopped_:
            backend.model.Model.ScheduleRoutine(self_routine)
        backend.model.Model.ReleaseLock(schedule_subscriptions=False)
        self.mutex_.release()
            
    def ScheduleExpired(self, self_routine):
        new_routines = []
        self.mutex_.acquire()
        for routine, add_time in self.routines_:
            if (self.time_ - add_time >= routine.GetSleepTime()):
                routine.Schedule()
            else:
                new_routines += [(routine, add_time)]
        self.routines_ = new_routines 
        self.mutex_.release()        

    def Add(self, routine):
        self.mutex_.acquire()
        self.routines_ += [(routine, self.time_)]
        self.mutex_.release()
