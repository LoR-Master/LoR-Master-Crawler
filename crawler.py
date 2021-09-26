from Models import riot
from Models import network
from Models import setting
from Models.setting import Server
from Models import utility
from Models import local
from Models import leaderboard

import os
import git
import json
import datetime
import threading
import time


class Crawler:
    def __init__(self, server):
        self.server = server
        self.setting = setting.Setting()
        self.setting.setServer(self.server)
        self.network = network.Network(self.setting)
        self.riot = riot.Riot(self.network)
        # asia europe americas
        leaderboard.updateAll()
        self.board = leaderboard.getboard(self.server)
        self.masterFullName = {}
        self.localTag = local.Local(setting)
        self.loadJson()
        self.getFull(self.getMasterPlayersNames())

    def loadJson(self):
        try:
            with open('save/' + self.server + '.json', 'r', encoding='utf-8') as fp:
                self.masterFullName = json.load(fp)
        except IOError as e:
            print('No cache found', e)
            return

    def save(self):
        with open(self.server + '.json', 'w+', encoding='utf-8') as fp:
            json.dump(self.masterFullName, fp, ensure_ascii=False, indent=2)

    def getMasterPlayersNames(self):
        masterNames = []
        for player in self.board:
            masterNames.append(player['name'])
        return masterNames

    def getNameFromMatches(self, name, tag):
        puuid = self.riot.getPlayerPUUID(name, tag)
        matchIds = self.riot.getMatchs(puuid)
        winNum = 0
        matchNum = 0
        if matchIds is None:
            print("MatchIDs empty", name, tag)
            return

        for matchid in matchIds:
            if matchNum == 20:
                break
            details = self.riot.getDetail(matchid)

            if details is None:
                continue

            if details['info']['game_type'] != 'Ranked':
                continue

            # print(details)
            twoPuuid = details['metadata']['participants']
            for puuid in twoPuuid:
                name = self.riot.getPlayerName(puuid)
                print(name)
                # check if name or tag is None
                if name[0] is not None and name[1] is not None:
                    self.masterFullName[name[0]] = name[1]
                self.save()

    def updateTagByName(self, name):
        with open(('Resource/' + self.server + '.dat'),
                  encoding="utf8") as search:
            for line in search:
                fullName = line.rstrip().split('#')
                if name == fullName[0]:
                    return fullName[1]
        return None

    def getTagByName(self, name):
        tag = self.masterFullName.get(name)
        # if tag is None:
        #     tag = self.updateTagByName(name)
        #     print(name, tag, 'From YI list')
        print('getTagByName: ', name, '#', tag)
        return tag

    def getFull(self, masterNames):
        print(masterNames)
        for name in masterNames:
            tag = self.getTagByName(name)
            if tag is None:
                continue
            self.getNameFromMatches(name, tag)
            # print(self.masterFullName)
            print(self.server, len(self.masterFullName), 'found')


def f(s):
    Crawler(s)


n = threading.Thread(target=f, args=(Server.NA,))
n.start()


e = threading.Thread(target=f, args=(Server.EU,))
e.start()


a = threading.Thread(target=f, args=(Server.ASIA,))
a.start()


def validateJSONFile(filePath):
    try:
        with open(filePath) as f:
            dataDict = json.load(f)
            os.makedirs('save', exist_ok=True)
            with open('save/' + filePath, 'w+', encoding='utf-8') as fp:
                json.dump(dataDict, fp, ensure_ascii=False, indent=2)
    except Exception as e:
        print(filePath, 'invalid json!')
        return None


jsonFileName = ['americas.json', 'asia.json', 'europe.json',
                'americasmatchDetails.json', 'europematchDetails.json', 'asiamatchDetails.json']


def saveGithub():
    for fileName in jsonFileName:
        validateJSONFile(fileName)
    try:
        repo = git.Repo("")
        repo.git.config('--global', 'user.name', "LMT [bot]")
        repo.git.add('--all')
        repo.git.commit('-m', 'test commit')
        
        repo.git.push()
    except Exception as e:
        print('saveGithub error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', e)
        return
    print('Pushed#############################################')

while True:
    saveGithub()
    time.sleep(600)
