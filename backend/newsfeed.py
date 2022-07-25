from backend.wheels.subscriptable import Subscriptable, notifier
import backend.model
import threading

class Post:
    def __init__(self, author, time, header, body):
        self.author_ = author
        self.time_ = time
        self.header_ = header
        self.body_ = body
        
    def GetAuthor(self):
        return self.author_
    def GetTime(self):
        return self.time_
    def GetHeader(self):
        return self.header_
    def GetBody(self):
        return self.body_
    def __str__(self):
        return str(self.time_)+":"+str(self.author_)+":"+str(self.header_)+":"+str(self.body_)

class Forum:
    def __init__(self, name):
        self.name_ = name
        self.feed_ = []
    
    def SendPost(self, author, header, body):
        p = Post(author, backend.model.Model.GetTimer().GetTime(), header, body)
        self.feed_.append(p)
    
    def GetPosts(self):
        return self.feed_
    
class NewsFeed (Subscriptable):

    def __init__(self, forums):
        super().__init__()
        self.forums_ = dict([(n,Forum(n)) for n in forums])
    
    def __getstate__(self):
        state = self.__dict__.copy()
        del state["mutex_"]
        del state["changed_"]
        return state
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.changed_ = False
        self.mutex_ = threading.Lock()
    
    def GetPosts(self, forum):
        return self.forums_[forum].GetPosts()
    
    @notifier
    def SendPost(self, forum, author, header, body):
        self.forums_[forum].SendPost(author, header, body)

