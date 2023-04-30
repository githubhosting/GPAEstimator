import csv
import json

d = []
s = set()
data = json.load(open("sis/IS/2021/SEM_03.json"))
for dat in data:
    if not dat: continue
    subs = dat["marks"]
    sd = {"usn": dat["usn"]}
    for sub, info in subs.items():
        sd[sub] = info["attd"]
        s.add(sub)
    d.append(sd)
with open("is_2021_sem3_attd.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["usn"] + sorted(s))
    writer.writeheader()
    writer.writerows(d)
