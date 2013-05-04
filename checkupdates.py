#!/usr/bin/pytho

MC_VERSION = "1.5.1"
BOT_URL = "http://bot.notenoughmods.com/%s.json"

import urllib2
import json

def main():
    data = file("/Users/admin/Downloads/1.5.1.json").read()#urllib2.urlopen(BOT_URL % (MC_VERSION,)).read()
    mods = json.loads(data)
    for mod in mods:
        name = mod["name"]
        version = mod["version"]
        print name,version

if __name__ == "__main__":
    main()

