import json

def loadJson():
    try:
        with open('europeMatchDetails' + '.json', 'r') as fp:
            matches = json.load(fp)
            print('total matches: ', len(matches))
            return matches
    except IOError as e:
        print('No cache found', e)
        return

noneMatchNum = 0
matches = loadJson()
rankMatches = {}
for key in matches:
    if matches[key] is None:
        noneMatchNum += 1
        continue
    if matches[key]["info"]["game_type"] == "Ranked":
        rankMatches[key] = matches[key]


print('ranked matches: ', len(rankMatches), 'none matches: ', noneMatchNum)

def validateJSONFile(filePath):
    try:
        with open(filePath) as f:
            return json.load(f)
    except Exception as e:
        print(filePath + 'invalid json: %s' % e)
        return None

jsonFileName = ['americas.json', 'asia.json', 'asia.json', 'americasmatchDetails.json', 'europematchDetails.json', 'asiamatchDetails.json']


def saveGithub():
    for fileName in jsonFileName:
        if validateJSONFile(fileName) is None:
            print(fileName, 'invalidated')

saveGithub()
