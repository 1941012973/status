import yaml, os, sys
from requests import head

issues = []
restored = []
nstatus = {}


def get_status_code(url):
    try:
        return head(url)
    except:
        return False


try:
    ostatus = yaml.load(open("_data/status.yml"), Loader=yaml.FullLoader)
except:
    open("_data/status.yml", "a").close()
    ostatus = yaml.load(open("_data/status.yml"), Loader=yaml.FullLoader)

try:
    tracker = yaml.load(open("_data/tracker.yml"), Loader=yaml.FullLoader)
except:
    print("_tracker.yml not found. Cannot check for status.")

for group in tracker:
    gname = group["group"]
    print("Running status check for group {}".format(gname))
    nstatus[gname] = {}
    nstatus[gname]["sites"] = {}
    for site in group["sites"]:
        sname = site["name"]
        print("Checking: " + sname)
        c = get_status_code(site["url"])
        if c and c.status_code >= 200 and c.status_code < 300:
            is_restored = (
                gname in ostatus
                and sname in ostatus[gname]["sites"]
                and ostatus[gname]["sites"][sname] != "operational"
            )
            if is_restored:
                restored.append(sname)
            nstatus[gname]["sites"][sname] = "operational"
        else:
            ostatus[gname] = {} if gname not in ostatus else ostatus[gname]
            ostatus[gname]["sites"] = (
                {} if "sites" not in ostatus[gname] else ostatus[gname]["sites"]
            )
            if sname in ostatus[gname]["sites"]:
                if ostatus[gname]["sites"][sname] == "operational":
                    nstatus[gname]["sites"][sname] = "partial"
                    issues.append(sname)
                else:
                    nstatus[gname]["sites"][sname] = "major"
            else:
                nstatus[gname]["sites"][sname] = "partial"

for status in nstatus:
    s = nstatus[status]["sites"].values()
    partial = "partial" if "partial" in s else None
    check = "major" if "major" in s else partial

    if check is None:
        nstatus[status]["group-status"] = "operational"
    else:
        nstatus[status]["group-status"] = check

header = []
for status in nstatus:
    s = nstatus[status]["group-status"]
    header.append(s)

if "major" in header:
    nstatus["statement"] = "We are suffering a major outage"
    nstatus["status-class"] = "critical"
elif "major" not in header and "partial" in header:
    nstatus["statement"] = "We are suffering a partial outage"
    nstatus["status-class"] = "partial"
elif "major" not in header and "partial" not in header and "operational" in header:
    nstatus["statement"] = "All systems are operational"
    nstatus["status-class"] = "no-issues"

f = open("_data/status.yml", "w+")
f.write(yaml.dump(nstatus))
f.close()

f = open("_data/issues.yml", "w+")
f.write(yaml.dump(issues))
f.close()

f = open("_data/restored.yml", "w+")
f.write(yaml.dump(restored))
f.close()
