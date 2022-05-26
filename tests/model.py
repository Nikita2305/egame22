from backend.model import Model
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
import time
import unittest

class NamedGraph (Subscriptable):
    
    def __init__(self):
        self.name_ = ""
        super().__init__() 
    
    @notifier
    def SetName(self, name):
        self.name_ = name

class ChangeNameRoutine (Executable):

    def __init__(self, new_name):
        self.new_name = new_name
        super().__init__()

    def __call__(self, routine):
        Model.AcquireLock()
        Model.GetGraph().name_ = self.new_name
        Model.ReleaseLock() 

class Test1_UnitModel (unittest.TestCase):

    def setUp(self):
        Model.instance_ = None
        Model.GetInstance().graph_ = NamedGraph()
        Model.Run()

    def tearDown(self):
        Model.GetTimer().Stop()

    def test1_simple_routine(self):
        import time
        start = time.time()
        sleep_time = 1
        expected_time = sleep_time + 0.5
        ITER = 100
        old_name = Model.GetGraph().name_
        expected_name = "user defined name"

        Model.AcquireLock()
        Model.ScheduleRoutine(Routine(ChangeNameRoutine(expected_name), sleep_time))
        Model.ReleaseLock()

        ok = False
        name = None
        for i in range(100):
            time.sleep(expected_time / ITER)
            Model.AcquireLock()
            name = Model.GetGraph().name_
            Model.ReleaseLock()
            if (name != old_name):
                ok = True
                break
        if (ok): 
            self.assertEqual(expected_name, name)
            self.assertTrue(time.time() - start < expected_time)
        else:
            self.assertTrue(False)         

class CounterGraph (Subscriptable):

    def __init__(self):
        self.counter_ = 0
        super().__init__()

    @notifier
    def Increase(self, dt):
        self.counter_ += dt

    def Get(self):
        return self.counter_

def ChangeCounter(routine):
    Model.AcquireLock()
    Model.GetGraph().Increase(1)
    Model.ReleaseLock()

class Test2_StressModel (unittest.TestCase):

    def setUp(self):
        Model.instance_ = None
        Model.GetInstance().graph_ = CounterGraph()
        Model.Run()

        self.startTime = time.time()

    def tearDown(self):
        Model.GetTimer().Stop()

        t = time.time() - self.startTime
        print('\n%s: %.3f' % (self.id(), t))

    def test1_stress_routine(self):
        expected_time = 1
        THREADS = 1000
        expected_ans = THREADS

        for i in range(THREADS):
            Model.AcquireLock()
            Model.ScheduleRoutine(Routine(ChangeCounter))
            Model.ReleaseLock()

        time.sleep(expected_time)
        Model.AcquireLock()
        ans = Model.GetGraph().Get()
        Model.ReleaseLock()
        self.assertEqual(expected_ans, ans)

    def test2_locking_costs(self):
        expected_time = 1
        THREADS = 1000
        ITER = 100
        expected_ans = THREADS

        for i in range(THREADS):
            Model.AcquireLock()
            Model.ScheduleRoutine(Routine(ChangeCounter))
            Model.ReleaseLock()

        ok = False
        for i in range(ITER):
            time.sleep(expected_time / ITER)
            Model.AcquireLock()
            ans = Model.GetGraph().Get()
            Model.ReleaseLock()
            if (expected_ans == ans):
                ok = True
                break

        if not ok:
            self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
