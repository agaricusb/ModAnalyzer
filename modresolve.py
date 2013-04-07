#!/usr/bin/python

import os
import sys
import pprint

import modanalyzer
import modlist

"""Get an available block ID."""
def findAvailable(used):
    # first available (one-fit)
    # TODO: bin packing algorithms, for multiple contiguous IDs - first, last, best, worst, almost worst fits
    for i in range(1, 4096):
        if i not in used:
            return i
    print used
    assert False, "all the blocks are used!"        # if you manage to max out the blocks in legitimate usage, I'd be interested in your mod collection

"""Get two mod names sorted by their ID resolution priority."""
def sortModByPriority(a, b):
    return cmp(a.lower(), b.lower())

"""Get whether this mod list contains a vanilla override, which should not be resolved."""
def vanillaOverride(sortedMods):
    for s in sortedMods:
        if s.startswith("Minecraft"):
            return True

    return False

def main():
    wantedMods = map(lambda x: os.path.join(modanalyzer.ALL_MODS_DIR, x), os.listdir(modanalyzer.ALL_MODS_DIR))

    contents = modanalyzer.load()

    slicedBlocks = modlist.sliceAcross(contents, "block")

    used = set(slicedBlocks.keys())
    mappings = []

    for id, usingMods in slicedBlocks.iteritems():
        if len(usingMods) > 1:
            sortedMods = usingMods.keys()
            sortedMods.sort(cmp=sortModByPriority)

            if vanillaOverride(sortedMods):
                continue

            print "Conflict at",id
            print "\tkeeping",sortedMods.pop()  # it gets the ID

            # Move other mods out of the way
            for conflictingMod in usingMods.keys():
                newId = findAvailable(used)
                used.add(newId)
                mappings.append((conflictingMod, "block", id, newId))
                print "\tmoving %s %s -> %s" % (conflictingMod, id, newId)

    pprint.pprint(mappings)

    sys.exit(0)

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
