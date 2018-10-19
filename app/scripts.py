### Imports ###
from collections import namedtuple
from app.logger import log
from app.db_queries import db_get_matchup_data_by_champion_ids
from operator import itemgetter


def get_matchup_data_by_champion_ids(allyId, enemyId):
    matchupData = db_get_matchup_data_by_champion_ids(allyId, enemyId)
    matchupDataList = []
    dataDict = {}
    for data in matchupData:
        dataDict = data.__dict__
        del dataDict['_sa_instance_state']
        del dataDict['id']
        winrate = float(float(dataDict['win']) / ( dataDict['win'] + dataDict['lose'] ))
        dataDict['winrate'] = winrate
        matchupDataList.append(dataDict)
        
    newList = sorted(matchupDataList, key=itemgetter('winrate'), reverse=True)
    return newList
    
### Date Functions ###
def get_time_datetime():
    return datetime.datetime.now()

def get_time_str():
    return str(datetime.datetime.now())

def str_to_datetime(s):
    return datetime.datetime.strptime(s,"%Y-%m-%d %H:%M:%S.%f")

def datetime_to_str(d):
    return str(d)

def dropUnicode(uObject):
    if type(uObject) == int:
        print("warning int input")
        uObject = str(uObject)

    elif not type(uObject) == str:
        strObject = None
        try:
            strObject = unicodedata.normalize('NFKD', uObject).encode('ascii','ignore')
        except:
            print("dropUnicode function exception")
        return strObject
    else:
        return uObject

if __name__ == '__main__':
    pass
