#!/usr/bin/pytho

MC_VERSION = "1.5.1"
BOT_URL = "http://bot.notenoughmods.com/%s.json"
ALL_MODS_DIR = "allmods"

import os
import urllib2
import json

import modanalyzer

def readLocalModVersions():
    for fn in os.listdir(ALL_MODS_DIR):
        path = os.path.join(ALL_MODS_DIR, fn)
        info = modanalyzer.readMcmodInfo(path)
        version = modanalyzer.getModVersion(fn, info)

        modid = modanalyzer.getModIDs(fn, info)

        print path, version, modid

def main():
    return readLocalModVersions()

    data = file("/Users/admin/Downloads/1.5.1.json").read()#urllib2.urlopen(BOT_URL % (MC_VERSION,)).read()
    mods = json.loads(data)
    for mod in mods:
        name = mod["name"]
        version = mod["version"]
        print name,version

if __name__ == "__main__":
    main()

