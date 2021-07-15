from Models import riot
from Models import network
from Models import setting
from Models.setting import Server
from Models import player
from Models import utility
from Models import local
from Models import leaderboard

import git
import json
import datetime
import threading
import time

class Crawler:
    def __init__(self, server):
        #self.server = Server.NA
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
            with open(self.server + '.json', 'r') as fp:
                self.masterFullName = json.load(fp)
        except IOError as e:
            print('No cache found', e)
            return


    def save(self):
        with open(self.server + '.json', 'w+', encoding='utf-8') as fp:
            json.dump(self.masterFullName, fp, ensure_ascii=False, indent=2)


    def createLog(self):
        with open('log.txt', 'a') as fp:
            now = datetime.datetime.now()
            now.strftime("%B %d, %Y")
            fp.write(str(now) + '\n')


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
            if matchNum == 10:
                break
            details = self.riot.getDetail(matchid)

            if details is None:
                continue

            # To-do add retry here
            if str(details).isdigit():
                continue

            if details['info']['game_type'] != 'Ranked':
                continue

            # print(details)
            twoPuuid = details['metadata']['participants']
            for count, puuid in enumerate(twoPuuid):
                name = self.riot.getPlayerName(puuid)
                print(name)
                self.masterFullName[name[0]] = name[1]
                full = [name[0], name[1]]
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
        if tag is None:
            tag = self.updateTagByName(name)
            print(name, tag, 'From YI list')
        print('getTagByName: ', name, tag)
        return tag


    def getFull(self, masterNames):
        print(masterNames)
        for name in masterNames:
            #self.saveGithub()
            tag = self.getTagByName(name)
            if tag is None:
                continue
            self.getNameFromMatches(name, tag)
            print(self.masterFullName)
            print('!!!!!!!!!', len(self.masterFullName), 'found')

    def saveGithub(self):
        self.createLog()
        repo = git.Repo("")
        repo.git.config('--global', 'user.name', "LMT[bot]" + self.server)
        repo.git.add('--all')
        repo.git.commit('-m', 'test commit')
        repo.git.push()

def f(s):
    Crawler(s)


n = threading.Thread(target=f, args = (Server.NA,))
n.start()


e = threading.Thread(target=f, args = (Server.EU,))
e.start()


a = threading.Thread(target=f, args = (Server.ASIA,))
a.start()

def saveGithub():
    with open('log.txt', 'a') as fp:
        now = datetime.datetime.now()
        now.strftime("%B %d, %Y")
        fp.write(str(now) + '\n')
    repo = git.Repo("")
    repo.git.config('--global', 'user.name', "LMT[bot]")
    repo.git.add('--all')
    repo.git.commit('-m', 'test commit')
    repo.git.push()


while True:
    print('Pushed################################')
    saveGithub()
    time.sleep(1200)