import re
import json

reg = 'a*'
result = [['a','b','b'],['c','d','e']]
all_pkgs = []

for row in result:
        package = {
            'Version': row[0],
            'Name': row[1],
            'ID': row[2]
        }
        all_pkgs.append(package)

all_pkgs = json.dumps(all_pkgs)
all_pkgs = json.loads(all_pkgs)

match_pkgs = []

for p in all_pkgs:
        currID = p['Name']
        if re.match(reg,currID) is not None:
            p.pop('ID')
            temp = p
            match_pkgs.append(temp)

print(match_pkgs)