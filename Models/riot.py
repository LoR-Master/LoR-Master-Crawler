import Models.network
import requests
import aiohttp
import asyncio
import json
import os


class Riot:
    def __init__(self, network):
        self.network = network
        self.server = self.network.setting.riotServer 
        self.asyncio = asyncio
        self.loop = None
        self.matchDetails = {}
        self.riotIds = {}
        self.playerNames = {}
        self.loadJson()
        self.session = requests.Session()
        return

    def loadJson(self):
        try:
            with open('save/'+ self.server + 'matchDetails.json', 'r', encoding='utf-8') as fp:
                self.matchDetails = json.load(fp)
            with open('data/' + self.server + 'riotIds.json', 'r', encoding='utf-8') as fp:
                self.riotIds = json.load(fp)
            with open('data/' + self.server + 'playerNames.json', 'r', encoding='utf-8') as fp:
                self.playerNames = json.load(fp)
        except IOError as e:
            print('No cache found', e)
            return

    def save(self):
        os.makedirs('data', exist_ok=True)
        with open(self.server + 'matchDetails.json', 'w+', encoding='utf-8') as fp:
            json.dump(self.matchDetails, fp, indent=2)
        with open('data/' + self.server + 'riotIds.json', 'w+', encoding='utf-8') as fp:
            json.dump(self.riotIds, fp)
        with open('data/' + self.server + 'playerNames.json', 'w+', encoding='utf-8') as fp:
            json.dump(self.playerNames, fp)

    # Should not use cache, because you cannot identify capital letters of playernames
    def getPlayerPUUID(self, name, tag):
        puuidLink = self.network.getPUUID(name, tag)
        masterId = self.network.setting.riotServer + name + tag + puuidLink

        if masterId in self.riotIds:
            return self.riotIds[masterId]
        print(puuidLink)
        try:
            puuidRequest = self.session.get(puuidLink)
        except requests.exceptions.RequestException as e:
            print(puuidLink)
            print(e)
            print('无法连接getPlayerPUUID服务器')
            return None
        idDetails = puuidRequest.json()
        header = puuidRequest.headers
        if not puuidRequest.ok:
            print(puuidLink)
            print(puuidRequest.headers)
            print(puuidRequest.status_code)
            print('userId -> PUUID服务器错误')
            print(idDetails)
            if 'Retry-After' in header:
                print('getPlayerPUUID服务器正忙', header['Retry-After'], '秒')
                Models.network.switchAPI()
            return None
        else:
            puuid = idDetails.get('puuid')
            gameName = idDetails.get('gameName')
            tagLine = idDetails.get('tagLine')
            if puuid is not None and gameName is not None:
                self.riotIds[masterId] = puuid
                self.playerNames[puuid] = gameName, tagLine
                self.save()
            return puuid

    def getPuuidWithoutCache(self, name, tag):
        puuidLink = self.network.getPUUID(name, tag)
        try:
            puuidRequest = self.session.get(puuidLink)
        except requests.exceptions.RequestException as e:
            print(puuidLink)
            print(e)
            print('无法连接getPlayerPUUID服务器')
            return None
        idDetails = puuidRequest.json()
        header = puuidRequest.headers
        if not puuidRequest.ok:
            print(puuidLink)
            print(puuidRequest.headers)
            print(puuidRequest.status_code)
            print('userId -> PUUID Error')
            print(idDetails)
            if 'Retry-After' in header:
                print('puuid busy', header['Retry-After'], '秒')
                Models.network.switchAPI()
                return header['Retry-After']
            return None
        else:
            puuid = idDetails.get('puuid') 
            return puuid

    def getMatchs(self, puuid):
        matchLink = self.network.getMatchsLink(puuid)
        try:
            matchRequest = self.session.get(matchLink)
        except requests.exceptions.RequestException as e:
            print(matchLink)
            print(e)
            print('无法连接比赛ID服务器')
            return None
        matchIds = matchRequest.json()
        header = matchRequest.headers
        if not matchRequest.ok:
            print(matchLink)
            print(matchRequest.headers)
            print(matchRequest.status_code)
            print('getmatchs服务器错误')
            print(matchIds)
            if 'Retry-After' in header:
                print('getmatchs服务器正忙', header['Retry-After'], '秒')
                Models.network.switchAPI()
            return None
        return matchIds

    async def aioMatchDetail(self, matchId):
        if matchId in self.matchDetails:
            return self.matchDetails[matchId]
        async with aiohttp.ClientSession() as session:
            try:
                detailsLink = self.network.getDetailsLink(matchId)
                async with session.get(detailsLink) as resp:
                    detail = await resp.json()
            except aiohttp.ClientConnectionError as e:
                print('aioMatchDetail Error: ', e)
                return None
        header = resp.headers
        if 'X-Method-Rate-Limit-Count' in header:
            print('X-Method-Rate-Limit-Count: ',
                  header['X-Method-Rate-Limit-Count'])
            print('X-App-Rate-Limit', header['X-App-Rate-Limit'])

        if 'Retry-After' in header:
            print('aio服务器正忙,请等待', header['Retry-After'], '秒')
            return header['Retry-After']

        if resp.ok:
            self.matchDetails[matchId] = detail
            self.save()
            return detail
        else:
            print('AIO比赛内容服务器错误: ', resp.status)
            print(detailsLink)
            print(detail)
            return None

    def getDetail(self, matchId):
        if matchId in self.matchDetails:
            return self.matchDetails[matchId]
        detailsLink = self.network.getDetailsLink(matchId)
        try:
            detailsRequest = self.session.get(detailsLink)
        except requests.exceptions.RequestException as e:
            print(detailsLink)
            print(e)
            print('无法连接比赛内容服务器')
            return None
        detail = detailsRequest.json()
        header = detailsRequest.headers
        if 'X-Method-Rate-Limit-Count' in header:
            print('X-Method-Rate-Limit-Count: ',
                  header['X-Method-Rate-Limit-Count'])
            print('X-App-Rate-Limit', header['X-App-Rate-Limit'])
        if not detailsRequest.ok:
            print(detailsLink)
            print(header)
            print(detailsRequest.status_code)
            print(detail)
            print('比赛内容服务器错误')
            if 'Retry-After' in header:
                print('服务器正忙,请等待', header['Retry-After'], '秒')
                second = header['Retry-After']
                # switchAPI will make crawler sleep, but the matchId is skipped
                Models.network.switchAPI(second)
                # retry after waiting, skipped matchId will be check again
                self.getDetail(self, matchId)
                return None
            if detailsRequest.status_code == 404:
                self.matchDetails[matchId] = None
                self.save()
            return None
        else:
            # this could still raise an AttributeError if example_dict['info'] exists but is not a dict
            gameType = detail.get('info', {}).get('game_type')
            if  gameType != 'Ranked':
                self.matchDetails[matchId] = None
                print(gameType, 'not support')
                return None
            else:
                try:
                    playerPuuids = detail['metadata']['participants']
                except Exception as e:
                    print('processMatchDetail error', e)
                playernames = []
                for puuid in playerPuuids:
                    name, tag = self.getPlayerName(puuid)
                    playernames.append(name + '#' + tag)
                detail['playernames'] = playernames                
                self.matchDetails[matchId] = detail
                self.save()
        return detail

    # 在main中使用和inspector中使用
    def getPlayerName(self, puuid):
        if puuid in self.playerNames:
            return self.playerNames[puuid]
        nameLink = self.network.getNameLink(puuid)
        try:
            nameRequest = self.session.get(nameLink)
        except requests.exceptions.RequestException as e:
            print(nameLink)
            print(e)
            print('无法连接puuid->userId服务器')
            return '名字Unknow', 'unknow'
        name = nameRequest.json()
        header = nameRequest.headers
        #headers = nameRequest.headers
        #print(headers)
        if not nameRequest.ok:
            print(nameLink)
            print(nameRequest.headers)
            print(nameRequest.status_code)
            print(name)
            print('puuid->userid服务器错误:')            
            if 'Retry-After' in header:
                print('服务器正忙,请等待', header['Retry-After'], '秒')
                Models.network.switchAPI()
            return 'Unknow', puuid
        else:
            self.playerNames[puuid] = name['gameName'], name['tagLine']
            self.save()
        return name['gameName'], (name['tagLine'])

    def getPlayerNameWithoutCache(self, puuid):
        nameLink = self.network.getNameLink(puuid)
        try:
            nameRequest = self.session.get(nameLink)
        except requests.exceptions.RequestException as e:
            print(nameLink)
            print(e)
            print('无法连接puuid->userId服务器')
            return '名字Unknow', 'unknow'
        name = nameRequest.json()
        header = nameRequest.headers
        #headers = nameRequest.headers
        #print(headers)
        if not nameRequest.ok:
            print(nameLink)
            print(nameRequest.headers)
            print(nameRequest.status_code)
            print(name)
            print('puuid->userid服务器错误:')            
            if 'Retry-After' in header:
                print('服务器正忙,请等待', header['Retry-After'], '秒')
                Models.network.switchAPI()
            return None
        else:
            self.playerNames[puuid] = name['gameName'], name['tagLine']
            self.save()
        return name['gameName'], (name['tagLine'])
