#!/usr/bin/python

import os
import sys
import pprint
import re

import modanalyzer
import modlist

CONFLICT_KINDS = ("block", "item", "biome")  # resolve conflicts on these

ID_RANGES = {
    "block": range(500, 4096), # >256 for future vanilla block expansion, >408 for future itemblocks -- maximum, 12-bit
    "item": range(5000, 32000),
    }

"""Get an available block ID."""
def findAvailable(used, kind):
    for i in ID_RANGES[kind]:
        if i not in used:
            return i
    print used
    assert False, "all %s are used!" % (kind,)        # if you manage to max out the blocks in legitimate usage, I'd be very interested in your mod collection

def sortModsByPriority(mods, allSortedMods):
    def getPriority(m):
        if m.startswith("Minecraft"): return -1
        return allSortedMods.index(modanalyzer.getModName(m.replace(".csv", "")))

    mods.sort(cmp=lambda a, b: cmp(getPriority(b), getPriority(a)))

"""Get whether this mod list contains a vanilla override, which should not be resolved."""
def vanillaOverride(mods):
    for m in mods:
        if m.startswith("Minecraft"):
            return True

    return False

"""Get a list of edits of tuples (mod,kind,id,newId) to resolve ID conflicts of 'kind'."""
def getConflictMappings(contents, kind, allSortedMods):
    slicedContent = modlist.sliceAcross(contents, kind)

    used = set(slicedContent.keys())
    mappings = []

    for id, usingMods in slicedContent.iteritems():
        if kind == "item" and id < 4096: continue # skip item blocks - TODO: instead check data isItemBlock

        if len(usingMods) > 1:
            sortedMods = usingMods.keys()
            sortModsByPriority(sortedMods, allSortedMods)

            if vanillaOverride(sortedMods):
                continue

            print "Conflict on %s at %s" % (kind, id)
            print "\tkeeping",sortedMods.pop()  # it gets the ID

            # Move other mods out of the way
            for conflictingMod in sortedMods:
                # first available (one-fit)
                # TODO: bin packing algorithms, for multiple contiguous IDs - first, last, best, worst, almost worst fits
                newId = findAvailable(used, kind)
                used.add(newId)
                mappings.append((conflictingMod.replace(".csv", ""), kind, id, newId))
                print "\tmoving %s %s -> %s" % (conflictingMod, id, newId)

    return mappings

CONFIG_IGNORE = ["forge.cfg", "forgeChunkLoading.cfg"]  # TODO: exclude from deps in mod analysis

"""Get list of source and target paths for config files of a given mod."""
def getConfigFiles(mod):
    configDir = modanalyzer.getConfigsDir(mod)

    configs = []
    for name in modanalyzer.recursiveListdir(configDir):
        if name in CONFIG_IGNORE: 
            continue
        sourcePath = os.path.join(configDir, name)
        targetPath = os.path.join(modanalyzer.TEST_SERVER_ROOT, "config", name)

        configs.append((sourcePath, targetPath))

    return configs

"""Install mod configuration. Returns any needed manual edits."""
def installModConfigs(mod, modMappings):
    pendingEdits = []

    # read default configs
    editingConfigs = {}
    for sourcePath, targetPath in getConfigFiles(mod):
        data = file(sourcePath).read()
        editingConfigs[targetPath] = data

    # apply edits
    for mod, kind, oldId, newId in modMappings:
        success = False
        for targetPath, data in editingConfigs.iteritems():
            data, thisFailed = applyConfigEdit(data, kind, oldId, newId)
            editingConfigs[targetPath] = data
            if not thisFailed: 
                success = True
                break

        if not success:
            pendingEdits.append((mod, kind, oldId, newId))


    # write files
    needsMerge = False
    for targetPath, data in editingConfigs.iteritems():
        print "Installing %s [%s]" % (targetPath, len(modMappings))
        modanalyzer.mkdirContaining(targetPath)

        if os.path.exists(targetPath):
            print "NOTICE: Mod reuses config: installing configs for %s from %s but %s already exists - needs merge" % (mod, sourcePath, targetPath)
            readme = "\n" + ("#" * 70) + "\n# TODO: Merge from " + modanalyzer.getModName(mod) + "\n" + ("#" * 70) + "\n"
            data = readme + data

            needsMerge = True
            pendingEdits += modMappings # probably everything, to be safe
            # TODO: try to merge automatically?

        file(targetPath, "a").write(data)

    return pendingEdits
   
"""Change given ID in read config file data, or add comments for the user to do it if it cannot be automated."""
def applyConfigEdit(data, kind, oldId, newId):
    section = None
    requiresManual = False

    if kind == "item":
        # ugh
        oldId -= 256
        newId -= 256

    # Find possibly matching lines
    hits = {}
    lines = data.split("\n")
    comments = []
    for i, line in enumerate(lines):
        line = line.replace("\n", "")
        if line.startswith("%s {" % (kind,)):
            section = kind

        if line.endswith("=%s" % (oldId)):
            replacement = re.sub(r"\d+$", str(newId), line)
            assert replacement != line, "Failed to replace matched config line %s for %s -> %s" % (line, oldId, newId)
            hits[i] = {"old": line, "new": replacement, "section": section, "matchingSection": section == kind}

    if len(hits) == 0:
        comments.append("# TODO: change %s ID %s -> %s" % (kind, oldId, newId))
        requiresManual = True
    elif len(hits) == 1:
        # just one hit, we know what to do
        n = hits.keys()[0]
        lines[n] = hits[n]["new"]
        comments.append("# Changed %s: %s -> %s" % (kind, hits[n]["old"], hits[n]["new"]))
    else:
        # ambiguous..
        # TODO: if there is only one matching section, use it! it is not ambiguous
        for n in hits.keys():
            comments.append("# TODO: Change %s -> %s, one of %s ID %s -> %s" % (hits[n]["old"], hits[n]["new"], kind, oldId, newId))
        requiresManual = True

    data = "\n".join(lines + comments)
    return data, requiresManual

"""Get an estimate of the relative amount of the content in a mod."""
def getModGirth(contents, mod):
    key = modanalyzer.getModName(mod) + ".csv"
    if not contents.has_key(key):
        print "No mod analysis found for %s, please analyze" % (mod,)
        sys.exit(-1)

    content = contents[key]

    blocks = content.get("block", [])

    girth = len(blocks) * 1000 + len(content) # TODO: more in-depth analysis, weights for different content types? (blocks > item?)

    return girth

PRIORITY_FILE = "priority.txt"

"""Sort all mods by priority."""
def sortAllMods(contents):
    mods = os.listdir(modanalyzer.ALL_MODS_DIR) 

    # default priority
    mods.sort(cmp=lambda a, b: cmp(getModGirth(contents, b), getModGirth(contents, a)))

    if os.path.exists(PRIORITY_FILE):
        existingPriority = [x.strip() for x in file(PRIORITY_FILE).readlines()]
        missing = set(mods) - set(existingPriority) 
        if len(missing) != 0:
            # just add to the end
            mods = existingPriority + list(missing)
            print "NOTICE: Adding %s mods to end of priority list %s" % (missing, PRIORITY_FILE)
            file(PRIORITY_FILE, "w").write("\n".join(mods))
        else:
            print "Reusing priority file %s" % (PRIORITY_FILE,)
            mods = existingPriority
    else:
        file(PRIORITY_FILE, "w").write("\n".join(mods))
        print "Wrote new priority file at %s, edit as you wish" % (PRIORITY_FILE,)

    return mods

def main():
    wantedMods = map(lambda x: os.path.join(modanalyzer.ALL_MODS_DIR, x), os.listdir(modanalyzer.ALL_MODS_DIR))

    contents = modanalyzer.load()

    allSortedMods = sortAllMods(contents)

    mappings = []
    for kind in CONFLICT_KINDS:
        mappings += getConflictMappings(contents, kind, allSortedMods)
    pprint.pprint(mappings)

    modsFolder, coremodsFolder, configFolder = modanalyzer.prepareCleanServerFolders(modanalyzer.TEST_SERVER_ROOT)

    requiresManual = {}
    for mod in wantedMods:
        if not contents.has_key(os.path.basename(mod)+".csv"):
            print "No mod analysis found for %s, please analyze" % (mod,)
            sys.exit(-1)

        print "Installing",mod
        modanalyzer.installMod(mod, modsFolder, coremodsFolder)

        modMappings = filter(lambda m: m[0] == os.path.basename(mod), mappings)

        pendingEdits = installModConfigs(mod, modMappings)
        if len(pendingEdits) > 0:
            requiresManual[mod] = pendingEdits

    if len(requiresManual) > 0:
        print "=" * 70
        for m, edits in requiresManual.iteritems():
            print m, "\t", " ".join([x[1] for x in getConfigFiles(m)]), "\t", edits
        print "=" * 70
        print "The above mods require manual configuration file editing to continue."
        print "Edit their configs appropriately (search for 'TODO'), then start the server."
    else:
        print "Ready to go..."
        modanalyzer.runServer()

if __name__ == "__main__":
    main()
