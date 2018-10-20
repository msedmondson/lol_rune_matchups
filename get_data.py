# RIOT API
# Goal: Find winrate of unique runepages vs champions in same lanePos

###                   ###
### Import Statements ###
###                   ###

import sys
import requests
import re
import xlrd
import os
import datetime
import csv
import time
from bs4 import BeautifulSoup
from lxml import html
import pandas as pd
import json
from app import scripts
from app.logger import log
from app.db_queries import db_merge_matchIds, db_merge_matchData, db_add_champions, db_add_runes, db_get_match_data_not_calculated, db_get_match_data, db_add_matchup_data, db_add_match_data_calculated, db_update_matchup_winrates, db_get_account_ids_by_matchid

# Import API Key from another file
from api_key import apiKey

###                  ###
### Global Variables ###
###                  ###

sleepDelayShort = 1.22  # Ideally, this is 1.2, but put extra 0.01 for safety
sleepDelayLong = 24.1  # Ideally, this is 1.2, but put extra 0.01 for safety
apiCount = 0
initializeDatabase = False

# curl --request GET 'https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/RiotSchmick?api_key=<key>' --include

def main(OUTPUT_PATH="./outfile.out"):
    
    ###      ###
    ### Main ###
    ###      ###

    log('Start Main')
    
    mySummonerId = '92280903'
    
    if(initializeDatabase):
        initialize_database(mySummonerId)
    
    matchId = 2794444102
    accountIds = db_get_account_ids_by_matchid(matchId)
    for accountId in accountIds.values():
        log("accountId")
        log(accountId)
        summoner = getSummonerByAccountId(accountId)
        summonerId = summoner['id']
        fill_database(summonerId)
    
    return # return main

###           ###
### Functions ###
###           ###

def initialize_database(summonerIdSeed):    
    ### Initialization ###
    # Key: int accountId
    # Value: dict of summoner information
    accountInfo = {}
    
    # List of unique accountIds
    listAccountIds = []
    
    # Key: int matchId
    # Value: array of accountIds
    matchIds = {}
    
    # Key: int matchId
    # Value: dict of full match data
    fullMatchData = {}
    
    # Key: int matchId
    # Value: dict of useful match data
    usefulMatchData = {}
    
    # Key: int participantId
    # Value: int accoundId
    participantIds = {}
    
    # Key: int runeId
    # Value: dict of useful rune data
    usefulRuneData = getUsefulRuneData()
    
    # Key: int championId
    # Value: dict of champion data
    championData = getChampionData()
    championData = championData['data']
    
    # Use my summonerId as a seed.
    summoner = getSummonerBySummonerId(summonerIdSeed)
    
    if(not summoner):
        log('Error: Summoner does not exist')
        return
    else:        
        accountInfo[summoner['accountId']] = summoner
    
    for accountId in accountInfo:
        listAccountIds = updateListAccountIds(listAccountIds, accountId)
    
    matchList = getMatchListByAccountId(listAccountIds[0])
    
    for match in matchList['matches']:
        matchIds[match['gameId']] = [listAccountIds[0]]
        
    ### Main Logic ###
    
    for matchId in matchIds:
        fullMatchData[matchId] = getMatchByMatchId(matchId)
    # fullMatchData[list(matchIds)[0]] = getMatchByMatchId(list(matchIds)[0])

    for match in fullMatchData:
        # I have no idea why I get this error:
        # 'bool' object has no attribute '__getitem__'
        # Need to put sleep here to fix.
        time.sleep(0.1)
        
        participantIdentities = fullMatchData[match]['participantIdentities']
        participants = fullMatchData[match]['participants']
        for participantId in participantIdentities:
            # Get participant Ids
            participantIds[participantId['participantId']] = participantId['player']['accountId']
            # Put account Ids in their respective matches if they are not already in the match
            accountId = participantId['player']['accountId']
            
            matchIds = updateMatchIds(matchIds, match, accountId)
            listAccountIds = updateListAccountIds(listAccountIds, accountId)
            
        for participant in participants:
            participantId = participant['participantId']
            accountId = participantIds[participantId]
            lanePos = participant['timeline']['lane']
            championId = participant['championId']
            stats = participant['stats']
            team = participant['teamId']
            win = stats['win']
            
            items = {}
            items['item0'] = stats['item0']
            items['item1'] = stats['item1']
            items['item2'] = stats['item2']
            items['item3'] = stats['item3']
            items['item4'] = stats['item4']
            items['item5'] = stats['item5']
            items['item6'] = stats['item6']
            
            runes = {}
            perkPrimaryStyle = {}
            perkSubStyle = {}
            
            perkPrimaryStyleId = stats['perkPrimaryStyle']
            perkSubStyleId = stats['perkSubStyle']
            
            perkPrimaryStyle['runePathId'] = perkPrimaryStyleId
            perkSubStyle['runePathId'] = perkSubStyleId
            
            listPerkIds = [stats['perk0'], stats['perk1'], stats['perk2'], stats['perk3'], stats['perk4'], stats['perk5']]
            
            flagRuneExists = True
            for idx, perkId in enumerate(listPerkIds):
                if(perkId not in usefulRuneData):
                    flagRuneExists = False
                    break
                else:    
                    rune = usefulRuneData[perkId]    
                    if(rune['runePathId'] == perkPrimaryStyleId):
                        perkPrimaryStyle[str('rune' + str(idx))] = perkId
                    else:
                        perkSubStyle[str('rune' + str(idx))] = perkId
            
            # If all runes exist
            if(flagRuneExists):
                runes['perkPrimaryStyle'] = { perkPrimaryStyleId: perkPrimaryStyle }
                runes['perkSubStyle'] = { perkSubStyleId: perkSubStyle }
                
                if( match not in usefulMatchData ):
                    usefulMatchData[match] = { 'accountIds': [] }
                usefulMatchData[match]['accountIds'].append( { accountId: { 'team': team, 'participantId': participantId, 'lanePos': lanePos, 'items': items, 'runes': runes, 'win': win, 'championId': championId } } )

    log("db_merge_matchIds")
    db_merge_matchIds(matchIds)
    log("db_merge_matchData")
    db_merge_matchData(usefulMatchData)
    log("db_add_champions")
    db_add_champions(championData)
    log("db_add_runes")
    db_add_runes(usefulRuneData)
    
    log("calculateMatchWinrates")
    calculateMatchWinrates()
    return
    
def fill_database(summonerIdSeed):    
    ### Initialization ###
    # Key: int accountId
    # Value: dict of summoner information
    accountInfo = {}
    
    # List of unique accountIds
    listAccountIds = []
    
    # Key: int matchId
    # Value: array of accountIds
    matchIds = {}
    
    # Key: int matchId
    # Value: dict of full match data
    fullMatchData = {}
    
    # Key: int matchId
    # Value: dict of useful match data
    usefulMatchData = {}
    
    # Key: int participantId
    # Value: int accoundId
    participantIds = {}
    
    # Key: int runeId
    # Value: dict of useful rune data
    usefulRuneData = getUsefulRuneData()
    
    # Key: int championId
    # Value: dict of champion data
    championData = getChampionData()
    championData = championData['data']
    
    # Use generated summoner ID as seed
    summoner = getSummonerBySummonerId(summonerIdSeed)
    
    if(not summoner):
        log('Error: Summoner does not exist')
    else:        
        accountInfo[summoner['accountId']] = summoner
    
    for accountId in accountInfo:
        listAccountIds = updateListAccountIds(listAccountIds, accountId)
    
    matchList = getMatchListByAccountId(listAccountIds[0])
    
    for match in matchList['matches']:
        matchIds[match['gameId']] = [listAccountIds[0]]
        
    ### Main Logic ###
    
    for matchId in matchIds:
        fullMatchData[matchId] = getMatchByMatchId(matchId)
    # fullMatchData[list(matchIds)[0]] = getMatchByMatchId(list(matchIds)[0])

    for match in fullMatchData:
        # I have no idea why I get this error:
        # 'bool' object has no attribute '__getitem__'
        # Need to put sleep here to fix.
        time.sleep(0.1)
        
        participantIdentities = fullMatchData[match]['participantIdentities']
        participants = fullMatchData[match]['participants']
        for participantId in participantIdentities:
            # Get participant Ids
            participantIds[participantId['participantId']] = participantId['player']['accountId']
            # Put account Ids in their respective matches if they are not already in the match
            accountId = participantId['player']['accountId']
            
            matchIds = updateMatchIds(matchIds, match, accountId)
            listAccountIds = updateListAccountIds(listAccountIds, accountId)
            
        for participant in participants:
            participantId = participant['participantId']
            accountId = participantIds[participantId]
            lanePos = participant['timeline']['lane']
            championId = participant['championId']
            stats = participant['stats']
            team = participant['teamId']
            win = stats['win']
            
            items = {}
            items['item0'] = stats['item0']
            items['item1'] = stats['item1']
            items['item2'] = stats['item2']
            items['item3'] = stats['item3']
            items['item4'] = stats['item4']
            items['item5'] = stats['item5']
            items['item6'] = stats['item6']
            
            runes = {}
            perkPrimaryStyle = {}
            perkSubStyle = {}
            
            # Sometimes, participants in matches don't have any perk data. Not sure why. Riot please fix.
            if('perkPrimaryStyle' not in stats):
                break
            perkPrimaryStyleId = stats['perkPrimaryStyle']
            perkSubStyleId = stats['perkSubStyle']
            
            perkPrimaryStyle['runePathId'] = perkPrimaryStyleId
            perkSubStyle['runePathId'] = perkSubStyleId
            
            listPerkIds = [stats['perk0'], stats['perk1'], stats['perk2'], stats['perk3'], stats['perk4'], stats['perk5']]
            
            flagRuneExists = True
            for idx, perkId in enumerate(listPerkIds):
                if(perkId not in usefulRuneData):
                    flagRuneExists = False
                    break
                else:    
                    rune = usefulRuneData[perkId]    
                    if(rune['runePathId'] == perkPrimaryStyleId):
                        perkPrimaryStyle[str('rune' + str(idx))] = perkId
                    else:
                        perkSubStyle[str('rune' + str(idx))] = perkId
            
            # If all runes exist
            if(flagRuneExists):
                runes['perkPrimaryStyle'] = { perkPrimaryStyleId: perkPrimaryStyle }
                runes['perkSubStyle'] = { perkSubStyleId: perkSubStyle }
                
                if( match not in usefulMatchData ):
                    usefulMatchData[match] = { 'accountIds': [] }
                usefulMatchData[match]['accountIds'].append( { accountId: { 'team': team, 'participantId': participantId, 'lanePos': lanePos, 'items': items, 'runes': runes, 'win': win, 'championId': championId } } )

    log("db_merge_matchIds")
    db_merge_matchIds(matchIds)
    log("db_merge_matchData")
    db_merge_matchData(usefulMatchData)
    
    log("calculateMatchWinrates")
    calculateMatchWinrates()
    return

# This function should calculate the winrates of champ vs champ per unique runepage
# Steps to follow:
# Iterate through MatchDataPerAccountId using matchId
# IF we find a unique runepage belonging to a single champion that is fighting another champion, we add that champion and the runes to MatchupData
# IF we find an identical matchup with runes in the table, then we do not add it to MatchupData
# Increment win or loss column in MatchupData    
def calculateMatchWinrates():
    matchDataSingle = db_get_match_data_not_calculated()
    while(len(matchDataSingle) > 0):
        matchDataSingle = matchDataSingle[0]
        
        matchDataMultiple = db_get_match_data(matchDataSingle.matchId)
        
        db_add_matchup_data(matchDataSingle, matchDataMultiple)

        db_add_match_data_calculated(matchDataSingle.id)
        
        matchDataSingle = db_get_match_data_not_calculated()
        
        updateWinrates()
    return
    


    
def returnResponse(response):
    if(response.ok):
        return (json.loads(response.content))
    else:
        return(False)

# def handleJsonResponse(jsonResponse):
    # if(not jsonResponse):
        # print('Error: Response does not exist')
    # else:
        # continue

def handleTimeDelay():
    # This first one is if I want to run API in chunks, rather than one at a time.
    # global apiCount
    # if(apiCount < 20):
        # apiCount += 1
    # else:
        # apiCount = 0
        # time.sleep(sleepDelayLong)
        
    time.sleep(sleepDelayShort)
    return
    
# Clean useful match data
# This function doesn't work. Keeping code for later use.
def cleanUsefulMatchData(usefulMatchData):
    for matchId in usefulMatchData:
        for accountId in usefulMatchData[matchId]:
            print(accountId)
            for stats in usefulMatchData[matchId][accountId]:
                if( (len( usefulMatchData[matchId][accountId][stats]['runes']['perkPrimaryStyle'] ) < 5) or (len( stats['runes']['perkSubStyle'] ) < 3) ):
                    usefulMatchData[matchId].pop(accountId, None)
    return usefulMatchData

def getUsefulRuneData():
    usefulRuneData = {}
    fullRuneList = getReforgedRuneList()
    for runePathDict in fullRuneList:
        runePathId = runePathDict['id']
        runePathName = runePathDict['name']
        for runeSlotDict in runePathDict['slots']:
            for runeDict in runeSlotDict['runes']:
                usefulRuneData[runeDict['id']] = { 'runePathName': runePathName, 'name': runeDict['name'], 'runePathId': runePathId }
    return usefulRuneData
    
def updateListAccountIds(listAccountIds, accountId):
    if(accountId not in listAccountIds):
        listAccountIds.append(accountId)
    return listAccountIds
    
def updateMatchIds(matchIds, matchId, accountId):
    if(accountId not in matchIds[matchId]):
        matchIds[matchId].append(accountId)
    return matchIds

def updateWinrates():
    db_update_matchup_winrates()
    return

###                ###
### RIOT API Calls ###
###                ###
    
def getSummonerBySummonerId(summonerId):
    url = 'https://na1.api.riotgames.com/lol/summoner/v3/summoners/' + str(summonerId) + '?api_key=' + apiKey
    r = requests.get(url)
    handleTimeDelay()
    return returnResponse(r)
    
def getSummonerByAccountId(accountId):
    url = 'https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-account/' + str(accountId) + '?api_key=' + apiKey
    r = requests.get(url)
    handleTimeDelay()
    return returnResponse(r)
    
def getMatchListByAccountId(accountId):
    url = 'https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/' + str(accountId) + '?api_key=' + apiKey
    r = requests.get(url)
    handleTimeDelay()
    return returnResponse(r)
    
def getMatchByMatchId(matchId):
    url = 'https://na1.api.riotgames.com/lol/match/v3/matches/' + str(matchId) + '?api_key=' + apiKey
    r = requests.get(url)
    handleTimeDelay()
    return returnResponse(r)

# This gets all the runes
def getReforgedRuneList():
    # Old URL
    # url = 'https://na1.api.riotgames.com/lol/static-data/v3/reforged-runes?api_key=' + apiKey
    
    # New URL
    url = 'https://ddragon.leagueoflegends.com/cdn/8.20.1/data/en_US/runesReforged.json'
    r = requests.get(url)
    handleTimeDelay()
    return returnResponse(r)
    
# This searches for runes (not rune paths like Resolve or Sorcery)    
### Warning: Old API Code. Function currently not being used.
def getReforgedRuneById(runeId):
    url = 'https://na1.api.riotgames.com/lol/static-data/v3/reforged-runes/' + str(runeId) + '?api_key=' + apiKey
    r = requests.get(url)
    handleTimeDelay()
    return returnResponse(r)
    
# This searches for runepaths
### Warning: Old API Code. Function currently not being used.
def getReforgedRunePathById(runePathId):
    url = 'https://na1.api.riotgames.com/lol/static-data/v3/reforged-rune-paths/' + str(runePathId) + '?api_key=' + apiKey
    r = requests.get(url)
    handleTimeDelay()
    return returnResponse(r)
    
def getChampionData():
    # Old URL
    # url ='https://na1.api.riotgames.com/lol/static-data/v3/champions?locale=en_US&dataById=true&api_key=' + apiKey
    
    # New URL
    url = 'http://ddragon.leagueoflegends.com/cdn/8.20.1/data/en_US/champion.json'
    r = requests.get(url)
    handleTimeDelay()
    return returnResponse(r)    
    
    
    
###             ###
### End of Main ###
###             ###    
    
if __name__ == "__main__":  # pragma: no cover
    main()