from backend.model import Model
from backend.subscription import Executable

class GraphChangedCallback (Executable):
    
    def __init__(self): 
        super().__init__()

    def Execute(self):
        print(f"New name: {Model.GetGraph().name_}")
