import json
import os
import sys
from app.models import AccountIdsPerMatchId, MatchDataPerAccountId, MatchupData, MatchDataCalculated, Champions, Runes, Serializer
from app import db
from random import randrange
from sqlalchemy.sql import exists
from sqlalchemy import text
from app.logger import log
from collections import namedtuple
import numpy as np


### MATCH_DATA Queries ###

def db_merge_matchIds(matchIds):
    for matchIdNum in matchIds:
        exists = AccountIdsPerMatchId.query.filter_by(matchId=matchIdNum).first()
        if(exists is None):
            if(len(matchIds[matchIdNum]) >= 10):
                data = AccountIdsPerMatchId(
                            matchId = matchIdNum,
                            accountId0 = matchIds[matchIdNum][0],
                            accountId1 = matchIds[matchIdNum][1],
                            accountId2 = matchIds[matchIdNum][2],
                            accountId3 = matchIds[matchIdNum][3],
                            accountId4 = matchIds[matchIdNum][4],
                            accountId5 = matchIds[matchIdNum][5],
                            accountId6 = matchIds[matchIdNum][6],
                            accountId7 = matchIds[matchIdNum][7],
                            accountId8 = matchIds[matchIdNum][8],
                            accountId9 = matchIds[matchIdNum][9])
                db.session.merge(data)
    db.session.commit()
    return

def db_merge_matchData(matchData):
    for match in matchData:
        for accountDict in matchData[match]['accountIds']:
            accountId = list(accountDict)
            accountId = accountId[0]
            # Check if record exists
            exists = MatchDataPerAccountId.query.filter_by(matchId=match, accountId=accountId).first()
            if(exists is None):
                runePrimary = accountDict[accountId]['runes']['perkPrimaryStyle']
                runePrimaryStyle = list(accountDict[accountId]['runes']['perkPrimaryStyle'])
                runePrimaryStyle = runePrimaryStyle[0]
                runeSub = accountDict[accountId]['runes']['perkSubStyle']
                runeSubStyle = list(accountDict[accountId]['runes']['perkSubStyle'])
                runeSubStyle = runeSubStyle[0]
                data = MatchDataPerAccountId(
                        matchId = match,
                        accountId = accountId,
                        team = accountDict[accountId]['team'],
                        championId = accountDict[accountId]['championId'],
                        participantId = accountDict[accountId]['participantId'],
                        lanePos = accountDict[accountId]['lanePos'],
                        win = accountDict[accountId]['win'],
                        item0 = accountDict[accountId]['items']['item0'],
                        item1 = accountDict[accountId]['items']['item1'],
                        item2 = accountDict[accountId]['items']['item2'],
                        item3 = accountDict[accountId]['items']['item3'],
                        item4 = accountDict[accountId]['items']['item4'],
                        item5 = accountDict[accountId]['items']['item5'],
                        item6 = accountDict[accountId]['items']['item6'],
                        runePriPath = runePrimaryStyle,
                        runePri0 = runePrimary[runePrimaryStyle]['rune0'],
                        runePri1 = runePrimary[runePrimaryStyle]['rune1'],
                        runePri2 = runePrimary[runePrimaryStyle]['rune2'],
                        runePri3 = runePrimary[runePrimaryStyle]['rune3'],
                        runeSubPath = runeSubStyle,
                        runeSub0 = runeSub[runeSubStyle]['rune4'],
                        runeSub1 = runeSub[runeSubStyle]['rune5'])
                db.session.merge(data)
    db.session.commit()
    return
    
def db_get_account_ids_by_matchid(matchId):
    result = AccountIdsPerMatchId.query.filter_by(matchId=matchId).first()
    accountIds = result.serialize()
    accountIds.pop('matchId', None)
    return accountIds
    
def db_get_all_matchIds():
    matchIds = AccountIdsPerMatchId.query.all()
    return matchIds

def db_add_champions(championData):
    for championId in championData:
        championInfo = championData[championId]
        # I know key and id are backwards, the old API used to have it like this...
        exists = Champions.query.filter_by(championId=championInfo['key']).first()
        if(exists is None):
            data = Champions(
                    championId = championInfo['key'],
                    key = championInfo['id'],
                    name = championInfo['name'])
            db.session.add(data)
    db.session.commit()
    return
    
def db_add_runes(runeData):
    for runeId in runeData:
        runeInfo = runeData[runeId]
        exists = Runes.query.filter_by(runeId=runeId).first()
        if(exists is None):
            data = Runes(
                    runeId = runeId,
                    name = runeInfo['name'],
                    runePathId = runeInfo['runePathId'],
                    runePathName = runeInfo['runePathName'])
            db.session.add(data)
    db.session.commit()
    return

def db_get_match_data(matchId):
    matchData = MatchDataPerAccountId.query.filter_by(matchId=matchId).all()
    return matchData
    
def db_get_match_data_not_calculated():
    sql = text('SELECT * FROM MATCH_DATA_PER_ACCOUNT_ID WHERE NOT EXISTS (SELECT 1 FROM MATCH_DATA_CALCULATED WHERE MATCH_DATA_CALCULATED.id = MATCH_DATA_PER_ACCOUNT_ID.id) LIMIT 1')
    result = db.engine.execute(sql)
    record = format_raw_sql_result(result)
    return record
    
def db_add_match_data_calculated(matchDataCalculatedId):
    data = MatchDataCalculated(id = matchDataCalculatedId)
    db.session.add(data)
    db.session.commit()
    return

def db_get_matchup_data_by_single_other(matchDataSingle, matchDataOther):
    matchupData = MatchupData.query.filter_by(
                    championId0 = matchDataSingle.championId,
                    championId1 = matchDataOther.championId,
                    runePriPath = matchDataSingle.runePriPath,
                    runePri0 = matchDataSingle.runePri0,
                    runePri1 = matchDataSingle.runePri1,
                    runePri2 = matchDataSingle.runePri2,
                    runePri3 = matchDataSingle.runePri3,
                    runeSubPath = matchDataSingle.runeSubPath,
                    runeSub0 = matchDataSingle.runeSub0,
                    runeSub1 = matchDataSingle.runeSub1).first()
    return matchupData
    
def db_add_matchup_data(matchDataSingle, matchDataMultiple):
    for matchDataOther in matchDataMultiple:
        if(matchDataSingle.id != matchDataOther.id):
            matchupData = db_get_matchup_data_by_single_other(matchDataSingle, matchDataOther)
            if(matchupData is None):
                # Get the champion IDs
                champion_id_0 = matchDataSingle.championId
                champion_id_1 = matchDataOther.championId
                
                # Get the champion names
                champion_name_0 = Champions.query.filter_by(championId=champion_id_0).first().name
                champion_name_1 = Champions.query.filter_by(championId=champion_id_1).first().name
                
                # Get the rune IDs
                rune_pri_path = matchDataSingle.runePriPath
                rune_pri_0 = matchDataSingle.runePri0
                rune_pri_1 = matchDataSingle.runePri1
                rune_pri_2 = matchDataSingle.runePri2
                rune_pri_3 = matchDataSingle.runePri3
                rune_sub_path = matchDataSingle.runeSubPath
                rune_sub_0 = matchDataSingle.runeSub0
                rune_sub_1 = matchDataSingle.runeSub1
                
                # Get the rune names
                rune_pri_path_name = Runes.query.filter_by(runeId=rune_pri_0).first().runePathName
                rune_pri_0_name = Runes.query.filter_by(runeId=rune_pri_0).first().name
                rune_pri_1_name = Runes.query.filter_by(runeId=rune_pri_1).first().name
                rune_pri_2_name = Runes.query.filter_by(runeId=rune_pri_2).first().name
                rune_pri_3_name = Runes.query.filter_by(runeId=rune_pri_3).first().name
                rune_sub_path_name = Runes.query.filter_by(runeId=rune_sub_0).first().runePathName
                rune_sub_0_name = Runes.query.filter_by(runeId=rune_sub_0).first().name
                rune_sub_1_name = Runes.query.filter_by(runeId=rune_sub_1).first().name
                
                data = MatchupData(
                    championId0 = champion_id_0,
                    championName0 = champion_name_0,
                    championId1 = champion_id_1,
                    championName1 = champion_name_1,
                    runePriPath = rune_pri_path,
                    runePriPathName = rune_pri_path_name,
                    runePri0 = rune_pri_0,
                    runePri0Name = rune_pri_0_name,
                    runePri1 = rune_pri_1,
                    runePri1Name = rune_pri_1_name,
                    runePri2 = rune_pri_2,
                    runePri2Name = rune_pri_2_name,
                    runePri3 = rune_pri_3,
                    runePri3Name = rune_pri_3_name,
                    runeSubPath = rune_sub_path,
                    runeSubPathName = rune_sub_path_name,
                    runeSub0 = rune_sub_0,
                    runeSub0Name = rune_sub_0_name,
                    runeSub1 = rune_sub_1,
                    runeSub1Name = rune_sub_1_name,
                    win = 0,
                    lose = 0,
                    winrate = 0)
                db.session.add(data)
                db.session.commit()
            
            matchupData = db_get_matchup_data_by_single_other(matchDataSingle, matchDataOther)
            
            db_update_matchup_data_win_by_id(matchupData.id, matchDataSingle.win, matchDataOther.win)
    return
    
    
def db_update_matchup_data_win_by_id(id, singleWin, otherWin):
    matchupData = MatchupData.query.get(id)
    if(singleWin == '0' and otherWin == '1'):
        matchupData.lose += 1
    else:
        matchupData.win += 1
    db.session.commit()
    
def db_update_matchup_winrates():
    sql = text('UPDATE MATCHUP_DATA SET winrate = CASE WHEN lose = 0 THEN 1 ELSE (win*1.0 / (win*1.0 + lose*1.0)) END')
    db.engine.execute(sql)
    return
    
def db_get_all_champions():
    return (Champions.query.all())
    
def db_get_matchup_data_by_champion_ids(allyId, enemyId):
    return MatchupData.query.filter_by(championId0=allyId, championId1=enemyId).all()
    
# def db_get_account_by_id
 
### Database Helpers ###
# Formats raw SQL into named tuple
def format_raw_sql_result(result):
    Record = namedtuple('Record', result.keys())
    records = [Record(*r) for r in result.fetchall()]
    return records 
    
# def db_merge_matchDataItems(matchData):
    # for match in matchData:
        # for accountDict in matchData[match]['accountIds']:
            # accountId = accountDict.keys()[0]
            # items = accountDict[accountId]['items']
            # data = MatchDataItemsPerAccountId(
                    # accountId = accountId,
                    # matchId = match,
                    # item0 = items['item0'],
                    # item1 = items['item1'],
                    # item2 = items['item2'],
                    # item3 = items['item3'],
                    # item4 = items['item4'],
                    # item5 = items['item5'],
                    # item6 = items['item6'])
            # db.session.merge(data)
    # db.session.commit()

# def db_merge_runes(matchData):



