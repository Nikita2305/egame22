from backend.model import Model
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
import time
import unittest

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

class IncreasingCallback (Executable):

    def __init__(self):
        self.value = 0

    def __call__(self):
        self.value += 1

class ObtainingCallback (Executable):
    
    def __init__(self):
        self.value = 0

    def __call__(self):
        Model.AcquireLock()
        self.value = Model.GetGraph().Get()
        Model.ReleaseLock()

class Test2_StressModel (unittest.TestCase):

    def setUp(self):
        time.sleep(0.1)
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
        Model.AcquireLock()
        for i in range(THREADS):
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

    def test3_time_management(self):
        expected_time = 2
        THREADS = 1000 # Not more than 1000
        expected_ans = THREADS
        import random
        Model.AcquireLock()
        for i in range(THREADS):
            Model.ScheduleRoutine(Routine(ChangeCounter, random.random() * expected_time))
        Model.ReleaseLock()
        time.sleep(expected_time + 0.2)
        Model.AcquireLock()
        ans = Model.GetGraph().Get()
        Model.ReleaseLock()
        self.assertEqual(expected_ans, ans)

    def test4_stress_subscriptions_called_once(self):
        expected_time = 1
        THREADS = 10
        subs = 5
        expected_ans = THREADS
        callbacks = []        

        Model.AcquireLock()
        for i in range(subs):
            callbacks += [IncreasingCallback()]
            Model.AddSubscription(Subscription(Model.GetGraph(), callbacks[-1]))
        for i in range(THREADS):
            Model.ScheduleRoutine(Routine(ChangeCounter, 0))
        Model.ReleaseLock()
        
        time.sleep(expected_time)
        for callback in callbacks:
            self.assertNotEqual(callback.value, 0)

    def test5_stress_subscriptions_final_value(self):
        expected_time = 1
        THREADS = 10
        subs = 5
        expected_ans = THREADS
        callbacks = []        

        Model.AcquireLock()
        for i in range(subs):
            callbacks += [ObtainingCallback()]
            Model.AddSubscription(Subscription(Model.GetGraph(), callbacks[-1]))
        for i in range(THREADS):
            Model.ScheduleRoutine(Routine(ChangeCounter, 0))
        Model.ReleaseLock()
        
        time.sleep(expected_time)
        for callback in callbacks:
            self.assertEqual(THREADS, callback.value)

if __name__ == '__main__':
    unittest.main()
