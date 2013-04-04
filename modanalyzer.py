#!/usr/bin/python

MC_VERSION = "1.5.1"
FORGE_VERSION = "7.7.1.624"

TEST_SERVER_ROOT = "temp-server"
TEST_SERVER_FILE = "minecraft_server+forge.jar"
TEST_SERVER_CMD = "java -mx2G -jar %s nogui"
ANALYZER_FILENAME = "ModAnalyzer-1.0-SNAPSHOT.jar"

ALL_MODS_DIR = "allmods"
DATA_DIR = "data"

import os, urllib, zipfile, urllib2, tempfile, shutil, json, hashlib, types, pprint, sys

def setupServer(serverFilename):
    mcZip = getURLZip("http://assets.minecraft.net/%s/minecraft_server.jar" % (MC_VERSION.replace(".", "_"),))
    forgeZip = getURLZip("http://files.minecraftforge.net/minecraftforge/minecraftforge-universal-%s-%s.zip" % (MC_VERSION, FORGE_VERSION))

    with zipfile.ZipFile(serverFilename, "w") as serverZip:
        for member in set(mcZip.namelist()) - set(forgeZip.namelist()):
            # vanilla classes, not overwritten
            serverZip.writestr(member, mcZip.read(member))
            print "M",member

        for member in set(forgeZip.namelist()) - set(mcZip.namelist()):
            # Forge classes
            serverZip.writestr(member, forgeZip.read(member))
            print "F",member

        for member in set(forgeZip.namelist()) & set(mcZip.namelist()):
            # overwrites - Forge > vanilla
            serverZip.writestr(member, forgeZip.read(member))
            print "O",member
    print "Server setup at",serverFilename

def getURLZip(url):
    f = tempfile.mktemp()
    print "Retrieving %s..." % (url,)
    urllib.urlretrieve(url, f)
    return zipfile.ZipFile(f, 'r')

def runServer():
    print "Starting server..."
    d = os.getcwd()
    os.chdir(TEST_SERVER_ROOT)
    os.system(TEST_SERVER_CMD % (TEST_SERVER_FILE,))
    os.chdir(d)
    print "Server terminated"

def analyzeMod(fn, others=[]):
    print "Analyzing %s..." % (fn,)
    # clean
    modsFolder = os.path.join(TEST_SERVER_ROOT, "mods")
    if os.path.exists(modsFolder):
        shutil.rmtree(modsFolder)
    os.mkdir(modsFolder)
    configFolder = os.path.join(TEST_SERVER_ROOT, "config")
    if os.path.exists(configFolder):
        shutil.rmtree(configFolder)

    # install analyzer
    shutil.copyfile(os.path.join("target", ANALYZER_FILENAME), os.path.join(modsFolder, ANALYZER_FILENAME))

    # install mod
    if fn is not None:
        shutil.copyfile(fn, os.path.join(modsFolder, getModName(fn)))

    # install deps
    for other in others:
        shutil.copyfile(other, os.path.join(modsFolder, getModName(other)))

    # running the server will load the analyzer, then quit
    runServer()

def getModName(fn):
    if fn is None:
        return "Minecraft-%s" % (MC_VERSION,)
    else:
        return os.path.basename(fn)

def getMods():
    if not os.path.exists(ALL_MODS_DIR):
        os.mkdir(ALL_MODS_DIR)
    mods = []
    for m in sorted(os.listdir(ALL_MODS_DIR)):
        if m.startswith("."): continue
        mods.append(os.path.join(ALL_MODS_DIR, m))
    return mods

def readMcmodInfo(fn):
    with zipfile.ZipFile(fn) as modZip:
        if "mcmod.info" in modZip.namelist():
            raw_json = modZip.read("mcmod.info")
            try:
                mcmod = json.loads(raw_json)
            except ValueError as e:
                #print raw_json
                #print "BROKEN JSON!",e,fn # FML uses a more lenient JSON parser than Python's json module TODO: be more lenient
                mcmod = []
        else:
            mcmod = []

        # Filename and hash is essential
        h = hashlib.sha256(file(fn).read()).hexdigest()
        mod = {"filename":fn, "sha256":h, "info":mcmod}
    return mod

"""Get submod dict from a top-level mod info dict from readMcmodInfo()."""
def getSubInfo(info):
    if isinstance(info["info"], types.DictType):
        subs = info["info"].get("modlist", [])  # AE - top-level dictionary
    else:
        subs = info["info"] # top-level array
    return subs

DEP_BLACKLIST = set((
    "mod_MinecraftForge",   # we always have Forge
    "Forge", # typo for mod_MinecraftForge

    "GUI_Api", # typo for GuiAPI and not needed on server
    ))

"""Get all dependent mod IDs from readMcmodInfo() result.""" # TODO: OO
def getDeps(info):
    deps = set()

    for sub in getSubInfo(info):
        deps.update(set(sub.get("dependencies", [])))
        deps.update(set(sub.get("dependancies", []))) # ohai iChun ;)

    deps = deps - DEP_BLACKLIST
    if "Industrialcraft" in deps: # GregTech
        deps.remove("Industrialcraft")
        deps.add("IC2")

    return deps

"""Get all mod IDs in an mcmod readMcmodInfo()."""
def getModIDs(info):
    ids = set()
    for sub in getSubInfo(info):
        if sub.has_key("modid"):
            ids.add(sub["modid"])
    return ids

def getInfoFilename(mod):
    return os.path.join(DATA_DIR, getModName(mod) + ".csv")

def saveModInfo(mod, skip):
    lines = []
    with file(getInfoFilename(mod), "w") as f:
        for line in file(os.path.join(TEST_SERVER_ROOT, "mod-analysis.csv")).readlines():
            notUs = False
            for s in skip:
                if line in s:
                    notUs = True
                    break

            if notUs:
                # skip content added by our dependencies
                continue

            f.write(line)
            lines.append(line)
    return lines


def main():

    forceRescan = False

    if len(sys.argv) > 1:
        if sys.argv[1] == "--force-rescan":
            forceRescan = True # TODO: proper argument parsing
        else:
            print "Usage: %s [--force-rescan]" % (sys.argv[0],)
            raise SystemExit

    # gather dependencies
    modid2fn = {}
    fn2deps = {}
    for fn in getMods():
        info = readMcmodInfo(fn)
        deps = getDeps(info)

        for modid in getModIDs(info):
            modid2fn[modid] = fn

        fn2deps[fn] = deps
        if len(deps) != 0:
            print fn,deps

    # build mod filename -> dependency filenames
    fn2depsfn = {}
    for fn, deps in fn2deps.iteritems():
        for dep in deps:
            if not modid2fn.has_key(dep):
                print "Mod %s is missing dependency: %s. Cannot continue" % (fn, dep)
                sys.exit(-1)

            fn2depsfn[fn] = modid2fn[dep]

        fn2depsfn[fn] = [modid2fn[dep] for dep in deps]


    # setup analyzer
    if not os.path.exists(os.path.join("target", ANALYZER_FILENAME)):
        os.system("mvn initialize -P -built")
        os.system("mvn package")

    # setup server
    server = os.path.join(TEST_SERVER_ROOT, TEST_SERVER_FILE)
    if not os.path.exists(server):
        if not os.path.exists(TEST_SERVER_ROOT):
            os.mkdir(TEST_SERVER_ROOT)
        setupServer(server)
    print "Using server at:",server

    # analyze vanilla for reference
    analyzeMod(None)
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
    vanilla = saveModInfo(None, [])
    analyzedMods = {None: vanilla}

    modsToAnalyze = getMods()
    while len(modsToAnalyze) > 0:
        mod = modsToAnalyze.pop()
        if not forceRescan and os.path.exists(getInfoFilename(mod)):
            print "Skipping",mod
            continue
        deps = fn2depsfn[mod]
        depsAnalyzed = [analyzedMods[None]]  # everything depends on vanilla
        for dep in deps:
            if len(fn2depsfn.get(dep, [])) > 0:
                print "Nested dependencies not yet supported, %s -> %s -> %s" % (mod, dep, fn2depsfn[dep]) # TODO: recurse
                sys.exit(-1)
            if not analyzedMods.has_key(dep):
                # need to analyze a dependency, take care of it
                analyzeMod(dep)
                analyzedMods[mod] = saveModInfo(mod, [analyzedMods]) # TODO: deps
                depsAnalyzed.append(analyzedMods[mod])
                if mod in modsToAnalyze: modsToAnalyze.remove(mod)
            else:
                # already analyzed this dependency, use it
                depsAnalyzed.append(analyzedMods[dep])
                
        analyzeMod(mod, deps)
        analyzedMods[mod] = saveModInfo(mod, depsAnalyzed)


if __name__ == "__main__":
    main()
