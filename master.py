from Models import leaderboard
import json

dict = {}

def loadJson():
    try:
        with open('data.json', 'r') as fp:
            global dict
            dict = json.load(fp)
    except IOError as e:
        print('No cache found', e)
        return

def save():
    with open('data.json', 'w+') as fp:
        global dict
        json.dump(dict, fp, indent=2)

leaderboard.updateAll()

board = leaderboard.leaderboards[0]['players']

masterNames = []

masterTags = {}

def getMasterPlayersNames():
    #print(board)
    for player in board:
        #print(player)
        masterNames.append(player['name'])
    print(masterNames)


all = []
noName = []

getMasterPlayersNames()
loadJson()
for name in masterNames:
    if name in dict:
        print(name, dict[name])
        all.append([name, dict[name]])
    else:
        noName.append(name + ' ' + str(masterNames.index(name)))
print('All Found: ', len(dict))
print('master: ', len(masterNames))
print('master found', len(all))

print(noName)


from Models import riot
from Models import network
from Models import setting
from Models.setting import Server
from Models import player
from Models import utility
from Models import local
from Models import leaderboard
import json
setting = setting.Setting()
setting.setServer(Server.NA)
network = network.Network(setting)
riot = riot.Riot(network)

changedName = []

def checkName(all):
    invalid = []
    for name in all.items():
        puuid = riot.getPuuidWithoutCache(name[0], name[1])
        if puuid is None:
            print(name)
            invalid.append(name)
            continue
    return invalid

    print('Invalid:', invalid)
    print('Changed Name', changedName)

def start(dict, save, checkName):
    wrong = checkName(dict)

    for a in wrong:
        del dict[a[0]]

    save()

#start(dict, save, checkName)
save()
