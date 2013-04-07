#!/usr/bin/python

import os
import sys
import pprint
import re

import modanalyzer
import modlist

START_BLOCK_ID = 500      # >256 for future vanilla block expansion, >408 for future itemblocks?
END_BLOCK_ID = 4095       # maximum, 12-bit

"""Get an available block ID."""
def findAvailable(used):
    # first available (one-fit)
    # TODO: bin packing algorithms, for multiple contiguous IDs - first, last, best, worst, almost worst fits
    for i in range(START_BLOCK_ID, END_BLOCK_ID + 1):
        if i not in used:
            return i
    print used
    assert False, "all the blocks are used!"        # if you manage to max out the blocks in legitimate usage, I'd be interested in your mod collection

"""Get two mod names sorted by their ID resolution priority."""
def sortModByPriority(a, b):
    #return cmp(a.lower(), b.lower())
    return cmp(b.lower(), a.lower())

"""Get whether this mod list contains a vanilla override, which should not be resolved."""
def vanillaOverride(sortedMods):
    for s in sortedMods:
        if s.startswith("Minecraft"):
            return True

    return False

"""Get a list of edits of tuples (mod,kind,id,newId) to resolve ID conflicts of 'kind'."""
def getConflictMappings(contents, kind):
    slicedContent = modlist.sliceAcross(contents, kind)

    used = set(slicedContent.keys())
    mappings = []

    for id, usingMods in slicedContent.iteritems():
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
                mappings.append((conflictingMod.replace(".csv", ""), kind, id, newId))
                print "\tmoving %s %s -> %s" % (conflictingMod, id, newId)

    return mappings

CONFIG_IGNORE = ["forge.cfg", "forgeChunkLoading.cfg"]  # TODO: exclude from deps in mod analysis

"""Get list of source and target paths for config files of a given mod."""
def getConfigFiles(mod):
    configDir = modanalyzer.getConfigsDir(mod)

    configs = []
    for name in os.listdir(configDir):
        if name in CONFIG_IGNORE: 
            continue
        sourcePath = os.path.join(configDir, name)
        targetPath = os.path.join(modanalyzer.TEST_SERVER_ROOT, "config", name)

        if os.path.isdir(sourcePath):
            continue

        configs.append((sourcePath, targetPath))

    return configs

"""Install mod configuration. Returns True if requires additional manual configuration by the user."""
def installModConfigs(mod, modMappings):

    requiresManual = False
    for sourcePath, targetPath in getConfigFiles(mod):
        if os.path.exists(targetPath):
            print "FATAL ERROR: installing configs for %s from %s but %s already exists, not overwriting" % (mod, sourcePath, targetPath)
            sys.exit(-1)
            # TODO: dep exclusion again

        data = file(sourcePath).read()

        data, thisRequiresManual = applyConfigEdits(data, modMappings)
        if thisRequiresManual: 
            requiresManual = True

        print "Installing %s -> %s [%s]" % (sourcePath, targetPath, len(modMappings))
        if requiresManual:
            print "NOTICE: manual edits required to %s" % (targetPath,)
        modanalyzer.mkdirContaining(targetPath)
        file(targetPath, "w").write(data)

    return requiresManual

   
"""Apply the required configuration edits to change the given IDs, as possible."""
def applyConfigEdits(data, modMappings):
    requiresManual = False
    for mod, kind, oldId, newId in modMappings:
        data, thisRequiresManual = applyConfigEdit(data, kind, oldId, newId)

        if thisRequiresManual: 
            requiresManual = True

    return data, requiresManual

"""Change given ID in read config file data, or add comments for the user to do it if it cannot be automated."""
def applyConfigEdit(data, kind, oldId, newId):
    section = None
    requiresManual = False

    # Find possibly matching lines
    hits = {}
    lines = data.split("\n")
    for i, line in enumerate(lines):
        line = line.replace("\n", "")
        if line.startswith("%s {" % (kind,)):
            section = kind

        if line.endswith("=%s" % (oldId)):
            hits[i] = {"old": line, "new": re.sub(r"\d+$", str(newId), line), "section": section, "matchingSection": section == kind}

    if len(hits) == 0:
        lines.append("# TODO: change %s ID %s -> %s" % (kind, oldId, newId))
        requiresManual = True
    elif len(hits) == 1:
        # just one hit, we know what to do
        n = hits.keys()[0]
        lines[n] = hits[n]["new"] + "   # was: " + hits[n]["old"].strip()
    else:
        # ambiguous..
        # TODO: if there is only one matching section, use it! it is not ambiguous
        for n in hits.keys():
            lines[n] += " # %s # TODO: change one of %s ID %s -> %s" % (hits[n]["new"], kind, oldId, newId)
        requiresManual = True

    data = "\n".join(lines)
    return data, requiresManual

def main():
    wantedMods = map(lambda x: os.path.join(modanalyzer.ALL_MODS_DIR, x), os.listdir(modanalyzer.ALL_MODS_DIR))

    contents = modanalyzer.load()

    mappings = getConflictMappings(contents, "block")
    pprint.pprint(mappings)

    modsFolder, coremodsFolder, configFolder = modanalyzer.prepareCleanServerFolders(modanalyzer.TEST_SERVER_ROOT)

    requiresManual = []
    for mod in wantedMods:
        if not contents.has_key(os.path.basename(mod)+".csv"):
            print "No mod analysis found for %s, please analyze" % (mod,)
            sys.exit(-1)

        print "Installing",mod
        modanalyzer.installMod(mod, modsFolder, coremodsFolder)

        modMappings = filter(lambda m: m[0] == os.path.basename(mod), mappings)
        pprint.pprint(mappings)

        if installModConfigs(mod, modMappings):
            requiresManual.append(mod)

    if len(requiresManual) > 0:
        print "=" * 70
        for m in requiresManual:
            print m, "\t", " ".join([x[1] for x in getConfigFiles(m)])
        print "=" * 70
        print "The above mods require manual configuration file editing to continue."
        print "Edit their configs manually appropriately, then start the server."
    else:
        print "Ready to go..."
        modanalyzer.runServer()

if __name__ == "__main__":
    main()
