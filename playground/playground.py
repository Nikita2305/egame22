from backend.model import Model
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.wheels.schedulers import ThreadScheduler
import time

# Setup:

from backend.market import Market, BaseTrend

def mcb(routine):
    print("market changed")

Model.GetInstance()
Model.GetInstance().market_ = Market(10, {
    "BTC" : BaseTrend(10000,1000), 
    "LTC" : BaseTrend(100,10), 
    "SGC" : BaseTrend(1000,500), 
})
Model.Run() # Spawns another thread
Model.AcquireLock()
Model.AddSubscription(Subscription(Model.GetMarket(), mcb))
Model.ReleaseLock()

time.sleep(16)
print(Model.GetMarket().time_)

print("BTC ",Model.GetMarket().GetHistory("BTC"))
print("LTC ",Model.GetMarket().GetHistory("LTC"))
print("SGC ",Model.GetMarket().GetHistory("SGC"))

print("BTC ",Model.GetMarket().GetPredict("BTC",10))
print("LTC ",Model.GetMarket().GetPredict("LTC",10))
print("SGC ",Model.GetMarket().GetPredict("SGC",10))

time.sleep(16)

print(Model.GetMarket().time_)

print("BTC ",Model.GetMarket().GetHistory("BTC"))
print("LTC ",Model.GetMarket().GetHistory("LTC"))
print("SGC ",Model.GetMarket().GetHistory("SGC"))

print("BTC ",Model.GetMarket().GetPredict("BTC",15))
print("LTC ",Model.GetMarket().GetPredict("LTC",15))
print("SGC ",Model.GetMarket().GetPredict("SGC",15))

print("bye")

def helloworld(routine):
    print("Hello world!")

#timer example
Model.AcquireLock()
r = Routine(helloworld, 5)
Model.ScheduleRoutine(r)
Model.ReleaseLock()
while not r.executed_:
    print(r.GetRemainingTime())
    time.sleep(1)

Model.GetTimer().Stop()
