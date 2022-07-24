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
        Model.GetGraph().SetName(self.new_name)
        Model.ReleaseLock() 

class NameChangedCallback (Executable):

    def __init__(self, lst):
        self.lst_ = lst

    def __call__(self, routine):
        self.lst_.append(1)

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
        expected_time = sleep_time + 0.2
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

    def test2_simple_subscription(self):
        sleep_time = 1
        expected_time = sleep_time + 0.2
        ITER = 100
        lst = list()

        Model.AcquireLock()
        Model.AddSubscription(Subscription(Model.GetGraph(), NameChangedCallback(lst)))
        Model.ScheduleRoutine(Routine(ChangeNameRoutine("hoho"), sleep_time))
        Model.ReleaseLock()

        time.sleep(expected_time)
        self.assertEqual(len(lst), 1)
    

if __name__ == '__main__':
    unittest.main()
