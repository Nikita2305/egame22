from backend.model import Model
import backend.events as events
from backend.wheels.routine import Routine

def a(r):
    Model.AcquireLock()
    try:

        forum = [
            "2ch",  # пишет и то, и то
            "4chan", # пишет про цены
            "habr"  # пишет про граф  
        ]

        author = [
            "Sigma", # пишет какой-нибудь спам
            "Роскомнадзор", # пишет про неполадки с графом
            "i_am_insider_228", # пишет фейки про маркет
            "wall_street_wolf", # пишет прогнозы про маркет
            "Непроверенный источник" # пишет что угодно 
        ]

        # Model.GetNewsFeed().SendPost(forum[0], author[0], '..topic..', '..message..')
        
        # Model.GetMarket().AddBump(cur="BTC",start=1,peak=5,end=10,amplitude=4)

    except Exception as ex:
        print(f"Event exception: {ex}")
    Model.ReleaseLock()

def init():
    time = 0
    lst = [
        (events.Always(),(Routine(a) if time == 0 else Routine(a, time)))
    ]
    return lst
