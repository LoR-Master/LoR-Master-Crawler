import json

def loadJson():
    try:
        with open('americasmatchDetails' + '.json', 'r') as fp:
            matches = json.load(fp)
            print('total matches: ', len(matches))
            return matches
    except IOError as e:
        print('No cache found', e)
        return

matches = loadJson()
rankMatches = {}
for key in matches:
    if matches[key]["info"]["game_type"] == "Ranked":
        rankMatches[key] = matches[key]


print('ranked matches: ', len(rankMatches))


