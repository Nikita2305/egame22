from backend.model import Model
import backend.events as events
from backend.wheels.routine import Routine

def a(r):
    Model.AcquireLock()
    print("bump here")
    Model.GetMarket().AddBump("BTC",0,3,10,4)
    Model.ReleaseLock()

def init():
    lst = [
        (events.Coincidence([
            events.CheckPrice("SGC",lambda x: x > 2000),
            events.CheckPrice("BTC",lambda x: x < 9000),
        ]),Routine(a))
    ]
    return lst
