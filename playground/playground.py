from backend.model import Model
from backend.callbacks.example import GraphChangedCallback
from backend.subscription import Subscription

# Setup:
Model.AddSubscription(Subscription(Model.GetGraph(), GraphChangedCallback()))

# In some routine:
Model.AcquireLock()
Model.GetGraph().SetName("helloworld")
Model.ReleaseLock()

