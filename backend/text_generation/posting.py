import os
from backend.text_generation.rus_text_generator import TextGenerator
from backend.wheels.routine import Executable, Routine
from backend.model import Model

class Floodilka (Executable):
    
    def __init__(self, forum_number):
        super().__init__()
        path = os.path.dirname(__file__)
        self.forum_number = forum_number
        self.text_generator = TextGenerator(path + "/result_1.rus", path + "/char_to_idx_1.pickle", path + "/idx_to_char_1.pickle")

    def __call__(self, routine):
        #print("fuck1")
        Model.AcquireLock()
        Model.GetNewsFeed().SendPost(self.forum_number, " ".join(self.text_generator.get_words(2)), " ".join(self.text_generator.get_words(3)), self.text_generator.get_cute_message(500))
        #print("fuck2")
        Model.ScheduleRoutine(routine)
        #print("fuck3")
        Model.ReleaseLock()
          
