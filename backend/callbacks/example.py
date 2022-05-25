from backend.model import Model
from backend.routine import Executable

class GraphChangedCallback (Executable):
    
    def __init__(self): 
        super().__init__()

    def __call__(self, nan):
        print(f"New name: {Model.GetGraph().name_}")
