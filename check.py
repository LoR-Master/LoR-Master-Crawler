from Models import leaderboard
from Models import riot
from Models import network
from Models import setting
from Models.setting import Server
from Models import leaderboard
import threading
import json


class Check:
    
    def __init__(self, server = Server.NA) -> None:
        self.server = server
        self.setting = setting.Setting()
        self.setting.setServer(self.server)
        self.network = network.Network(self.setting)
        self.riot = riot.Riot(self.network)
        self.dict = {}
        leaderboard.updateAll()

        self.board = leaderboard.getboard(self.server)

        self.masterNames = []

        self.masterTags = {}


        self.all = []
        self.noName = []

        self.getMasterPlayersNames()
        self.loadJson()

        self.showNum()
        self.start()
        self.save()

    def loadJson(self):
        try:
            with open('save/' + self.server + '.json', 'r') as fp:
                self.dict = json.load(fp)
        except IOError as e:
            print('No cache found', e)
            return

    def save(self):
        with open('save/' + self.server + '.json', 'w+', encoding='utf-8') as fp:
            json.dump(self.dict, fp, ensure_ascii=False, indent=2)

    def getMasterPlayersNames(self):
        #print(board)
        for player in self.board:
            #print(player)
            self.masterNames.append(player['name'])
        #print(self.masterNames)

    def showNum(self):
        for name in self.masterNames:
            if name in self.dict:
                #print(name, self.dict[name])
                self.all.append([name, self.dict[name]])
            else:
                self.noName.append(name + ' ' + str(self.masterNames.index(name)))
        print('All Found: ', len(self.dict))
        print('master: ', len(self.masterNames))
        print('master found', len(self.all))

        print(self.noName)

    def checkName(self):
        invalid = []
        for name in self.dict.items():
            puuid = self.riot.getPuuidWithoutCache(name[0], name[1])
            if puuid is None:
                # print(name)
                invalid.append(name)
                continue
        return invalid

        print('Invalid:', invalid)

    def start(self):
        wrong = self.checkName()
        for a in wrong:
            del self.dict[a[0]]
        self.save()

def f(s):
    Check(s)

n = threading.Thread(target=f, args = (Server.NA,))
n.start()


e = threading.Thread(target=f, args = (Server.EU,))
e.start()


a = threading.Thread(target=f, args = (Server.ASIA,))
a.start()
