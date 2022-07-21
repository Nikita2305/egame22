from backend.wheels.subscriptable import Subscriptable, notifier

class Team (Subscriptable):
    def __init__(self, token, name, currencies):
        super().__init__()
        self.name_ = name
        self.token_ = token
        self.cryptowallet_ = dict([(cur,0.) for cur in currencies])
        self.wallet_ = 0.
        self.actions_ = 0.
        
    def GetCryptoMoney(self, cur):
        return self.cryptowallet_[cur]
    @notifier
    def AddCryptoMoney(self, cur, amount):
        self.cryptowallet_[cur] += amount
    def AddCryptoMoneyCheck(self, cur, amount):
        return self.cryptowallet_[cur] + amount >= 0
    
    def GetMoney(self):
        return self.wallet_
    @notifier
    def AddMoney(self, amount):
        self.wallet_ += amount
    def AddMoneyCheck(self, amount):
        return self.wallet_ + amount >= 0
    
    def GetActions(self):
        return self.actions_
    @notifier
    def AddActions(self, amount):
        self.actions_ += amount
    def AddActionsCheck(self, amount):
        return self.actions_ + amount >= 0
    
    def GetName(self):
        return self.name_
    @notifier
    def SetName(self, name):
        self.name_ = name

class TeamsManager:
    def __init__(self, currencies):
        self.teams_ = dict()
        self.currencies_ = currencies
    def GetTeam(self, token):
        return self.teams_[token]
    def GetTeamByName(self, name):
        for t in self.teams_:
            if t.GetName() == name:
                return t
        raise ValueError
    def CreateTeam(self, token, name=None):
        if name is None:
            name = "Team "+str(len(self.teams_)+1)
        self.teams_[token] = Team(token, name, self.currencies_)
