#!/usr/bin/python

import os
import sys

import modanalyzer

def main():
    wantedMods = map(lambda x: os.path.join(modanalyzer.ALL_MODS_DIR, x), os.listdir(modanalyzer.ALL_MODS_DIR))

    contents = modanalyzer.load()

    modsFolder, coremodsFolder, configFolder = modanalyzer.prepareCleanServerFolders(modanalyzer.TEST_SERVER_ROOT)


    for mod in wantedMods:
        if not contents.has_key(os.path.basename(mod)+".csv"):
            print "No mod analysis found for %s, please analyze" % (mod,)
            sys.exit(-1)

        print "Installing",mod
        modanalyzer.installMod(mod, modsFolder, coremodsFolder)
        # TODO: resolve conflicts

    #modanalyzer.runServer()

if __name__ == "__main__":
    main()
