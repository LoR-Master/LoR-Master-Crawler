from Models import riot
from Models import network
from Models import setting
from Models.setting import Server
from Models import player
from Models import utility
from Models import local
from Models import leaderboard

import json
import datetime
now = datetime.datetime.now()
now.strftime("%B %d, %Y")

def loadJson():
    try:
        with open('data.json', 'r') as fp:
            global masterFullName
            masterFullName = json.load(fp)
    except IOError as e:
        print('No cache found', e)
        return


def save():
    with open('data.json', 'w+') as fp:
        json.dump(masterFullName, fp)

def log():
    with open('log.txt', 'a') as fp:
        now = datetime.datetime.now()
        now.strftime("%B %d, %Y")
        fp.write(str(now))

def getMasterPlayersNames():
    for player in board:
        masterNames.append(player['name'])

def getParticipantsPuuids(name, tag):
    puuid = riot.getPlayerPUUID(name, tag)
    matchIds = riot.getMatchs(puuid)
    winNum = 0
    matchNum = 0
    if matchIds is None:
        print("MatchIDs empty", name, tag)
        return

    for matchid in matchIds:
        if matchNum == 3:
            break
        details = riot.getDetail(matchid)

        if details is None:
            continue

        #To-do add retry here
        if str(details).isdigit():
            continue

        if details['info']['game_type'] != 'Ranked':
            continue

        # print(details)
        twoPuuid = details['metadata']['participants']
        for count, puuid in enumerate(twoPuuid):
            name = riot.getPlayerName(puuid)
            print(name)
            masterFullName[name[0]] = name[1]
            full = [name[0], name[1]]
            save()


def getTagByName(name):
    tag = masterFullName.get(name)
    if tag is None:
        localTag.updateTagByName(name)
        tag = localTag.opponentTag
        print(name, tag, 'From YI list')
    print(name, tag)
    return tag

import git

def getFull():
    print(masterNames)
    for name in masterNames:
        log()
        repo = git.Repo("")
        repo.git.config('--global', 'user.name', "LoR-Master-Tracker/LoR-Player-Crawler")
        repo.git.add('--all')
        repo.git.commit('-m', 'test commit')
        repo.git.push()
        tag = getTagByName(name)
        if tag is None:
            continue
        getParticipantsPuuids(name, tag)
        print(masterFullName)
        save()
        print('!!!!!!!!!', len(masterFullName), 'found')




setting = setting.Setting()
setting.setServer(Server.NA)
network = network.Network(setting)
riot = riot.Riot(network)
# asia europe americas
leaderboard.updateAll()
board = leaderboard.leaderboards[0]['players']
masterNames = []
masterFullName = {}
localTag = local.Local(setting)
loadJson()
getMasterPlayersNames()
getFull()
