import json

jsonFileName = ['americasmatchDetails.json', 'europematchDetails.json', 'asiamatchDetails.json']

jsonPlayerName = ['americas.json', 'asia.json', 'asia.json']

def loadJson(fileName):
    try:
        with open('' + fileName, 'r') as fp:
            matches = json.load(fp)
            print(fileName, 'total matches: ', len(matches))
            return matches
    except Exception as e:
        print('No cache found', e)
        return


def analyse(fileName):
    noneMatchNum = 0
    matches = loadJson(fileName)
    if matches is None:
        return
    rankMatches = {}
    for key in matches:
        if matches[key] is None:
            noneMatchNum += 1
            continue
        if matches[key]["info"]["game_type"] == "Ranked":
            rankMatches[key] = matches[key]


    print('ranked matches: ', len(rankMatches), 'none matches: ', noneMatchNum)


for fileName in jsonFileName:
    print(fileName)
    analyse(fileName)






# def validateJSONFile(filePath):
#     try:
#         with open(filePath) as f:
#             return json.load(f)
#     except Exception as e:
#         print(filePath + 'invalid json: %s' % e)
#         return None




# def saveGithub():
#     for fileName in jsonFileName:
#         if validateJSONFile(fileName) is None:
#             print(fileName, 'invalidated')

# saveGithub()
