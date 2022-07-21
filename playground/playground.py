from backend.model import Model
from backend.wheels.routine import Executable, Routine
from backend.wheels.subscriptable import Subscription, Subscriptable, notifier
from backend.wheels.schedulers import ThreadScheduler
from backend.events import EventManager

import backend.libevents.BTChype

import time

# Setup:

from backend.market import Market, BaseTrend
from backend.teams import TeamsManager

def mcb(routine):
    print("market changed")
    print("BTC ",Model.GetMarket().GetExchangeRate("BTC"),
          "LTC ",Model.GetMarket().GetExchangeRate("LTC"),
          "SGC ",Model.GetMarket().GetExchangeRate("SGC"))

Model.GetInstance()
Model.GetInstance().market_ = Market(10, {
    "BTC" : BaseTrend(10000,1000), 
    "LTC" : BaseTrend(100,10), 
    "SGC" : BaseTrend(1000,500), 
})

Model.GetInstance().teams_ = TeamsManager(["BTC","LTC","SGC"])
Model.GetTeams().CreateTeam("A")
Model.GetTeams().CreateTeam("B")
Model.GetTeams().CreateTeam("C")

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

def money(r,name):
    print(name,"has",Model.GetTeams().GetTeam(name).GetCryptoMoney("LTC"))

Model.AcquireLock()
Model.AddSubscription(Subscription(Model.GetTeams().GetTeam("A"), lambda r: money(r,"A")))
Model.AddSubscription(Subscription(Model.GetTeams().GetTeam("B"), lambda r: money(r,"B")))
Model.AddSubscription(Subscription(Model.GetTeams().GetTeam("C"), lambda r: money(r,"C")))
Model.ReleaseLock()

event_manager = EventManager()

event_manager.LoadEvent("BTChype")
event_manager.LaunchEvent("BTChype")

time.sleep(5)
Model.AcquireLock()
Model.GetTeams().GetTeam("A").AddCryptoMoney("LTC", 10)
Model.GetTeams().GetTeam("B").AddCryptoMoney("LTC", 100)
Model.ReleaseLock()
time.sleep(5)
Model.GetTeams().GetTeam("B").AddCryptoMoney("LTC", -80,"test")
time.sleep(5)
print(Model.GetTeams().GetTeam("B").GetLog())
print(Model.GetTeams().GetTeam("B").GetLog(reason="test"))
print(Model.GetTeams().GetTeam("B").GetLog(subject="LTC"))
print(Model.GetTeams().GetTeam("B").GetLog(reason="sss"))

time.sleep(600)

print("BTC ",Model.GetMarket().GetHistory("BTC"))
print("LTC ",Model.GetMarket().GetHistory("LTC"))
print("SGC ",Model.GetMarket().GetHistory("SGC"))

Model.GetTimer().Stop()


