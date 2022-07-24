from backend.model import Model
import backend.events as events
from backend.wheels.routine import Routine

def a(r):
    Model.AcquireLock()
    Model.GetNewsFeed().SendPost('2ch', 'ivan', 'test', 'test message')
    Model.ReleaseLock()

def init():
    lst = [
        (events.Always(),Routine(a))
    ]
    return lst
