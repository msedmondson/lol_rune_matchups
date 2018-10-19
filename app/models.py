from app import db, app
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired
import json
from sqlalchemy.inspection import inspect

class AccountIdsPerMatchId(db.Model):
    __tablename__  = 'ACCOUNT_IDS_PER_MATCH_ID'
    
    matchId = db.Column(db.Integer, primary_key=True)
    accountId0 = db.Column(db.Integer, nullable=True) # 207192489
    accountId1 = db.Column(db.Integer, nullable=True)
    accountId2 = db.Column(db.Integer, nullable=True)
    accountId3 = db.Column(db.Integer, nullable=True)
    accountId4 = db.Column(db.Integer, nullable=True)
    accountId5 = db.Column(db.Integer, nullable=True)
    accountId6 = db.Column(db.Integer, nullable=True)
    accountId7 = db.Column(db.Integer, nullable=True)
    accountId8 = db.Column(db.Integer, nullable=True)
    accountId9 = db.Column(db.Integer, nullable=True)
    
    # Tip: You don't actually need to do an constructor override
    # def __init__()
        
    def get_id(self):
        return unicode(self.matchId)
        
    def serialize(self):
        d = Serializer.serialize(self)
        return d

class MatchDataPerAccountId(db.Model):
    __tablename__  = 'MATCH_DATA_PER_ACCOUNT_ID'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matchId = db.Column(db.Integer, nullable=False) # 207192489
    accountId = db.Column(db.Integer, nullable=False)
    team = db.Column(db.Integer, nullable=True)
    championId = db.Column(db.Integer, nullable=True)
    participantId = db.Column(db.Integer, nullable=True)
    lanePos = db.Column(db.String(10), nullable=True)
    win = db.Column(db.String(10), nullable=True)
    item0 = db.Column(db.Integer, nullable=True)
    item1 = db.Column(db.Integer, nullable=True)
    item2 = db.Column(db.Integer, nullable=True)
    item3 = db.Column(db.Integer, nullable=True)
    item4 = db.Column(db.Integer, nullable=True)
    item5 = db.Column(db.Integer, nullable=True)
    item6 = db.Column(db.Integer, nullable=True)
    runePriPath = db.Column(db.Integer, nullable=True)
    runePri0 = db.Column(db.Integer, nullable=True)
    runePri1 = db.Column(db.Integer, nullable=True)
    runePri2 = db.Column(db.Integer, nullable=True)
    runePri3 = db.Column(db.Integer, nullable=True)
    runeSubPath = db.Column(db.Integer, nullable=True)
    runeSub0 = db.Column(db.Integer, nullable=True)
    runeSub1 = db.Column(db.Integer, nullable=True)
    
    def get_id(self):
        return unicode(self.id)
        
class MatchupData(db.Model):
    __tablename__ = 'MATCHUP_DATA'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    championId0 = db.Column(db.Integer, nullable=False)
    championName0 = db.Column(db.String(20), nullable=False)
    championId1 = db.Column(db.Integer, nullable=False)
    championName1 = db.Column(db.String(20), nullable=False)
    runePriPath = db.Column(db.Integer, nullable=True)
    runePriPathName = db.Column(db.String(25), nullable=True)
    runePri0 = db.Column(db.Integer, nullable=True)
    runePri0Name = db.Column(db.String(25), nullable=True)
    runePri1 = db.Column(db.Integer, nullable=True)
    runePri1Name = db.Column(db.String(25), nullable=True)
    runePri2 = db.Column(db.Integer, nullable=True)
    runePri2Name = db.Column(db.String(25), nullable=True)
    runePri3 = db.Column(db.Integer, nullable=True)
    runePri3Name = db.Column(db.String(25), nullable=True)
    runeSubPath = db.Column(db.Integer, nullable=True)
    runeSubPathName = db.Column(db.String(25), nullable=True)
    runeSub0 = db.Column(db.Integer, nullable=True)
    runeSub0Name = db.Column(db.String(25), nullable=True)
    runeSub1 = db.Column(db.Integer, nullable=True)
    runeSub1Name = db.Column(db.String(25), nullable=True)
    win = db.Column(db.Integer, nullable=False)
    lose = db.Column(db.Integer, nullable=False)
    winrate = db.Column(db.Float, nullable=True)
    
    # runePri0Name = db.relationship('Runes', secondary=MatchupDataRunes, backref=db.backref('runePri0Name', lazy = 'dynamic'))

    def get_id(self):
        return unicode(self.id)
        
class MatchDataCalculated(db.Model):
    __tablename__ = 'MATCH_DATA_CALCULATED'
    
    id = db.Column(db.Integer, primary_key=True)
       
    def get_id(self):
        return unicode(self.id)
        
class Champions(db.Model):
    __tablename__ = 'CHAMPIONS'
    
    championId = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(15), nullable=False)
    name = db.Column(db.String(15), nullable=False)

    def get_id(self):
        return unicode(self.championId)
        
class Runes(db.Model):
    __tablename__ = 'RUNES'
    
    runeId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    runePathId = db.Column(db.Integer, nullable=False)
    runePathName = db.Column(db.String(15), nullable=False)

    def get_id(self):
        return unicode(self.runeId)
        
class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}
        
    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
        
# class MatchDataItemsPerAccountId(db.Model):
    # __tablename__  = 'MATCH_DATA_ITEMS_PER_ACCOUNT_ID'
    
    # accountId = db.Column(db.Integer, primary_key=True)
    # matchId = db.Column(db.Integer, nullable=False) # 207192489
    # item0 = db.Column(db.Integer, nullable=True)
    # item1 = db.Column(db.Integer, nullable=True)
    # item2 = db.Column(db.Integer, nullable=True)
    # item3 = db.Column(db.Integer, nullable=True)
    # item4 = db.Column(db.Integer, nullable=True)
    # item5 = db.Column(db.Integer, nullable=True)
    # item6 = db.Column(db.Integer, nullable=True)
    
    # def get_id(self):
        # return unicode(self.accountId)
        
# class MatchDataRunesPerAccountId(db.Model):
    # __tablename__  = 'MATCH_DATA_RUNES_PER_ACCOUNT_ID'
    
    # accountId = db.Column(db.Integer, primary_key=True)
    # matchId = db.Column(db.Integer, nullable=False) # 207192489
    # item0 = db.Column(db.Integer, nullable=True)
    # item1 = db.Column(db.Integer, nullable=True)
    # item2 = db.Column(db.Integer, nullable=True)
    # item3 = db.Column(db.Integer, nullable=True)
    # item4 = db.Column(db.Integer, nullable=True)
    # item5 = db.Column(db.Integer, nullable=True)
    # item6 = db.Column(db.Integer, nullable=True)
    
    # def get_id(self):
        # return unicode(self.accountId)
        
  
        