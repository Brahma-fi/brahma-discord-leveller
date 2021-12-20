import json

karma = {}
with open("./out/user_karma.json", "r") as readfile:
    karma = json.load(readfile)

total_karma = 0

for user in list(karma.keys()):
    total_karma += karma[user]["karma"]

print(total_karma/len(list(karma.keys())))