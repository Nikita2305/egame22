from backend.wheels.subscriptable import Subscriptable, notifier
import backend.model

class LogEntry:
    def __init__(self, subject, reason, amount):
        self.subject_ = subject
        self.reason_ = reason
        self.amount_ = amount
        self.time_ = backend.model.Model.GetTimer().GetTime()

class Team (Subscriptable):
    def __init__(self, token, name, currencies, color):
        super().__init__()
        self.name_ = name
        self.color_ = color
        self.token_ = token
        self.cryptowallet_ = dict([(cur,0.) for cur in currencies])
        self.log_ = []
        self.wallet_ = 0.
        self.actions_ = 4
        
    def GetCryptoMoney(self, cur):
        return self.cryptowallet_[cur]
    @notifier
    def AddCryptoMoney(self, cur, amount, reason="unknown"):
        self.cryptowallet_[cur] += amount
        self.log_.append(LogEntry(cur,reason,amount))
    def AddCryptoMoneyCheck(self, cur, amount):
        return self.cryptowallet_[cur] + amount >= 0
    
    def GetMoney(self):
        return self.wallet_
    @notifier
    def AddMoney(self, amount, reason="unknown"):
        self.wallet_ += amount
        self.log_.append(LogEntry("money",reason,amount))
    def AddMoneyCheck(self, amount):
        return self.wallet_ + amount >= 0
    
    def GetActions(self):
        return self.actions_
    @notifier
    def AddActions(self, amount, reason="unknown"):
        self.actions_ += amount
        self.log_.append(LogEntry("actions",reason,amount))
    @notifier
    def SetActions(self, amount, reason="unknown"):
        self.actions_ = amount
        self.log_.append(LogEntry("actions",reason,amount))
    def AddActionsCheck(self, amount):
        return self.actions_ + amount >= 0
    
    def GetName(self):
        return self.name_
    @notifier
    def SetName(self, name):
        self.name_ = name
    
    def GetColor(self):
        return self.color_
    
    def GetLog(self, subject=None, reason=None):
        ret = self.log_
        if subject is not None:
            ret = [x for x in ret if x.subject_ == subject]
        if reason is not None:
            ret = [x for x in ret if x.reason_ == reason]
        return ret

class TeamsManager:
    def __init__(self, currencies):
        self.teams_ = dict()
        self.currencies_ = currencies
    def GetTeamsNames(self):
        return [self.teams_[x].GetName() for x in self.teams_]
    def GetTeam(self, token):
        return self.teams_[token]
    def GetTeamsList(self):
        teams = []
        for token in self.teams_.keys():
            teams.append(self.GetTeam(token))
        return teams
    def GetTeamByName(self, name):
        for t in self.teams_:
            if self.teams_[t].GetName() == name:
                return self.teams_[t]
        raise ValueError
    def CreateTeam(self, token, color, name=None):
        if name is None:
            name = "Team "+str(len(self.teams_)+1)
        self.teams_[token] = Team(token, name, self.currencies_, color)
    def GetTeamsList(self):
        return [self.teams_[x] for x in self.teams_]
