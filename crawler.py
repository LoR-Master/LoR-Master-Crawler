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

class Crawler:
    def __init__(self):
        self.server = Server.ASIA
        self.setting = setting.Setting()
        self.setting.setServer(self.server)
        self.network = network.Network(setting)
        self.riot = riot.Riot(network)
        # asia europe americas
        leaderboard.updateAll()
        self.board = leaderboard.leaderboards[0]['players']

        self.masterFullName = {}
        self.localTag = local.Local(setting)
        self.loadJson()
        self.getFull(self.getMasterPlayersNames())


    def loadJson(self):
        try:
            with open( self.server + '.json', 'r') as fp:
                global masterFullName
                masterFullName = json.load(fp)
        except IOError as e:
            print('No cache found', e)
            return


    def save(self):
        with open(self.server + '.json', 'w+') as fp:
            json.dump(masterFullName, fp, indent=2)


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
                masterFullName[name[0]] = name[1]
                full = [name[0], name[1]]
                self.save()


    def updateTagByName(self, name):
        with open(('Resource/' + self.setting.getServer() + '.dat'),
                encoding="utf8") as search:
            for line in search:
                fullName = line.rstrip().split('#')
                if name == fullName[0]:
                    return fullName[1]
        return None


    def getTagByName(self, name):
        tag = self.masterFullName.get(name)
        if tag is None:
            tag = self.localTag.updateTagByName(name)
            print(name, tag, 'From YI list')
        print('getTagByName: ', name, tag)
        return tag


    def getFull(self, masterNames):
        print(masterNames)
        for name in masterNames:
            self.saveGithub()
            tag = self.getTagByName(name)
            if tag is None:
                continue
            self.getNameFromMatches(name, tag)
            print(masterFullName)
            print('!!!!!!!!!', len(masterFullName), 'found')

    def saveGithub(self):
        self.createLog()
        repo = git.Repo("")
        repo.git.config('--global', 'user.name', "LMT[bot]")
        repo.git.add('--all')
        repo.git.commit('-m', 'test commit')
        repo.git.push()


Crawler()