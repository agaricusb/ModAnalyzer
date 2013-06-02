#!/usr/bin/python

# Check the NotEnoughMods mod list to compare the latest versions of mods with your versions

MC_VERSION = "1.5.1"
BOT_URL = "http://bot.notenoughmods.com/%s.json"
ALL_MODS_DIR = "allmods"

import os
import urllib2
import json
import sys

import modanalyzer
import mcmodfixes

def compareName2ModID(name, modid):
    print "compare",name,modid,
    if name.lower() == modid.lower(): return True
    if name.lower() == modid.lower().replace("mod_", ""): return True

    modid = mcmodfixes.fixNotEnoughModsName(modid)
    if name.lower() == modid.lower(): return True
    if name.lower() == modid.lower().replace("mod_", ""): return True

    return False

def lookupRemoteModVersion(modids, remoteMods):
    for mod in remoteMods:
        for modid in modids:
            if compareName2ModID(mod["name"], modid):
                print "HIT"
                return mod["version"]
            print "NOT"

    return None

def compareLocalMods(remoteMods, localRoots):
    FORMAT = "%s %-20s\t%-20s\t%s %s"
    print FORMAT % (" ", "REMOTE (Latest)", "LOCAL", "", "")
    for localRoot in localRoots:
        for fn in os.listdir(localRoot):
            if fn.startswith("."): continue
            if os.path.isdir(os.path.join(localRoot, fn)): continue
            if not fn.endswith(".zip") and not fn.endswith(".jar"): continue

            path = os.path.join(localRoot, fn)
            info = modanalyzer.readMcmodInfo(path)
            version = modanalyzer.getModVersion(fn, info)
            modid = modanalyzer.getModIDs(fn, info)

            remoteVersion = lookupRemoteModVersion(modid, remoteMods)

            # mark if versions differ
            # TODO: only if greater
            if remoteVersion != version:
                tag = "*"
            else:
                tag = " "

            print FORMAT % (tag, remoteVersion, version, path, modid)

def main():
    if len(sys.argv) == 1:
        localRoots = [ALL_MODS_DIR]
    else:
        localRoots = sys.argv[1:]

    data = file("/Users/admin/Downloads/1.5.1.json").read()
    #data = urllib2.urlopen(BOT_URL % (MC_VERSION,)).read()
    remoteMods = json.loads(data)

    compareLocalMods(remoteMods, localRoots)

if __name__ == "__main__":
    main()

