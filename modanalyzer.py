#!/usr/bin/python

MC_VERSION = "1.5.1"
FORGE_VERSION = "7.7.1.652"

TEST_SERVER_ROOT = "temp-server"
TEST_SERVER_FILE = "minecraft_server+forge.jar"
TEST_SERVER_CMD = "java -mx2G -jar %s nogui"
ANALYZER_FILENAME = "ModAnalyzer-1.0-SNAPSHOT.jar"

ALL_MODS_DIR = "allmods"
DATA_DIR = "data"
CONFIGS_DIR = "configs"

import os, urllib, zipfile, urllib2, tempfile, shutil, json, hashlib, types, pprint, sys

import mcmodfixes

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

def prepareCleanServerFolders(serverRoot):
    modsFolder = os.path.join(serverRoot, "mods")
    if os.path.exists(modsFolder): 
        shutil.rmtree(modsFolder)

    coremodsFolder = os.path.join(serverRoot, "coremods")
    if os.path.exists(coremodsFolder):
        shutil.rmtree(coremodsFolder)

    os.mkdir(modsFolder)
    os.mkdir(coremodsFolder)
    configFolder = os.path.join(serverRoot, "config")
    if os.path.exists(configFolder):
        shutil.rmtree(configFolder)

    return modsFolder, coremodsFolder, configFolder

def analyzeMod(fn, others=[]):
    print "Analyzing %s... (deps=%s)" % (getModName(fn), others)
    # clean
    modsFolder, coremodsFolder, configFolder = prepareCleanServerFolders(TEST_SERVER_ROOT)

    # install analyzer
    shutil.copyfile(os.path.join("target", ANALYZER_FILENAME), os.path.join(modsFolder, ANALYZER_FILENAME))

    # install mod
    installMod(fn, modsFolder, coremodsFolder)

    # install deps
    for other in others:
        installMod(other, modsFolder, coremodsFolder)

    # running the server will load the analyzer, then quit
    runServer()

def isCoremod(fn):
    return readMcmodInfo(fn)["isCoremod"]

def installMod(fn, modsFolder, coremodsFolder):
    if fn is None: 
        return

    if isCoremod(fn):
        dest = coremodsFolder
    else:
        dest = modsFolder

    instructionFolder = mcmodfixes.getInstructionFolder(os.path.basename(fn))
    if instructionFolder is not None:
        # we're not done yet..
        hoopJumper(fn, instructionFolder, dest)
    else:
        # simple and easy file copy
        shutil.copyfile(fn, os.path.join(dest, getModName(fn)))

"""Jump through extra hoops required to install a mod, such as extracting a specific folder in a specific location."""
def hoopJumper(fn, instructionFolder, dest):
    print "Extracting double-zipped mod",fn
    with zipfile.ZipFile(fn) as containerZip:
        for name in containerZip.namelist():
            parts = name.split(os.path.sep)
            if instructionFolder not in parts:
                # other documentation, etc.
                continue

            # cut path at the "Put in mods folder" folder
            n = parts.index(instructionFolder)
            path = os.path.sep.join(parts[n + 1:])
            if path.endswith("/") or len(path) == 0:
                #print "Creating",path
                _mkdir(os.path.join(dest, path))
                continue

            #print "Extracting",path
            data = containerZip.read(name)
            file(os.path.join(dest, path), "w").write(data)

"""Make the directory containing the given filename, if needed."""
def mkdirContaining(filename):
    parts = filename.split(os.path.sep)
    tail = parts[:-1]
    targetDir = os.path.sep.join(tail)

    _mkdir(targetDir)

# Borrowed from FML
#Taken from: http://stackoverflow.com/questions/7545299/distutil-shutil-copytree
def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

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

        if mcmodfixes.modNeedsRename(m):
            newName = uniquelyRenameMod(m)
            print "Renaming non-unique mod filename %s -> %s" % (m, newName)
            os.rename(os.path.join(ALL_MODS_DIR, m), os.path.join(ALL_MODS_DIR, newName))
            m = newName

        mods.append(os.path.join(ALL_MODS_DIR, m))
    return mods

"""Get a new hopefully more unique filename for mods named without their versions."""
def uniquelyRenameMod(fn):
    print "Getting unique filename for",fn
    info = readMcmodInfo(os.path.join(ALL_MODS_DIR, fn))
    assert info.has_key("info"), "Unable to read mcmod.info for: %s" % (fn,)
    assert type(info["info"]) == types.ListType, "No mcmod.info entries for: %s" % (fn,)
    assert len(info["info"]) == 1, "Not exactly one mcmod.info entry in: %s" % (fn,)
    assert info["info"][0].has_key("version"), "No version property in mcmod.info for" % (fn,)
    version = info["info"][0]["version"]

    original, ext = os.path.splitext(fn)

    return "%s-%s%s" % (original, version, ext)

def readMcmodInfo(fn):
    if not fn.endswith(".jar") and not fn.endswith(".zip"): print "WARNING: non-zip/jar mod in",fn
    with zipfile.ZipFile(fn) as modZip:
        if "mcmod.info" in modZip.namelist():
            raw_json = modZip.read("mcmod.info")
            try:
                mcmod = json.loads(raw_json)
            except ValueError as e:
                #print raw_json
                #print "This mod has unparseable JSON in mcmod.info:",e,fn # FML uses a more lenient JSON parser than Python's json module TODO: be more lenient
                mcmod = []
        else:
            mcmod = []

        if "META-INF/MANIFEST.MF" in modZip.namelist():
            isCoremod = "FMLCorePlugin" in modZip.read("META-INF/MANIFEST.MF")
            if isCoremod: print "Found coremod:",fn
        else:
            isCoremod = False

        # Filename and hash is essential
        h = hashlib.sha256(file(fn).read()).hexdigest()
        mod = {"filename":fn, "sha256":h, "info":mcmod, "isCoremod": isCoremod}
    return mod

"""Get submod dict from a top-level mod info dict from readMcmodInfo()."""
def getSubInfo(info):
    if isinstance(info["info"], types.DictType):
        subs = info["info"].get("modlist", [])  # AE, bspkrsCore - top-level dictionary
    else:
        subs = info["info"] # top-level array
    return subs

"""Get all dependent mod IDs from readMcmodInfo() result.""" # TODO: OO
def getDeps(fn, info):
    deps = set()

    for sub in getSubInfo(info):
        # https://github.com/MinecraftForge/FML/wiki/FML-mod-information-file

        # soft deps - lets require them anyways
        deps.update(set(sub.get("dependencies", []))) # before
        deps.update(set(sub.get("dependancies", []))) # typo
        deps.update(set(sub.get("dependants", []))) # after

        # hard deps
        deps.update(set(sub.get("requiredMods", [])))

    deps = mcmodfixes.fixDeps(getModName(fn), deps)

    return deps

"""Get all mod IDs in an mcmod readMcmodInfo()."""
def getModIDs(fn, info):
    ids = set()
    for sub in getSubInfo(info):
        if sub.has_key("modid"):
            ids.add(sub["modid"])
    return mcmodfixes.fixModIDs(getModName(fn), ids)

def getInfoFilename(mod):
    return os.path.join(DATA_DIR, getModName(mod) + ".csv")

def getConfigsDir(mod):
    return os.path.join(CONFIGS_DIR, getModName(mod))

"""Read the most recent analyzed mod unfiltered content lines."""
def readModInfo():
    return file(os.path.join(TEST_SERVER_ROOT, "mod-analysis.csv")).readlines()

"""Write mod info to disk given unfiltered readModInfo() and list of other mod info lines (deps) to exclude."""
def saveModInfo(mod, modLines, skip, allDeps):
    lines = []
    with file(getInfoFilename(mod), "w") as f:
        for line in modLines:
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

    if len(lines) == 0:
        print "*" * 70
        print "WARNING: No content found in mod",mod  # maybe a non-content mod.. or maybe improperly installed?
        print "*" * 70

    # save default config
    if os.path.exists(getConfigsDir(mod)): 
        shutil.rmtree(getConfigsDir(mod))
    os.mkdir(getConfigsDir(mod))

    # filter deps configs
    ignoreConfigs = []
    for dep in allDeps:
        depConfigs = os.listdir(getConfigsDir(dep))
        print mod,dep,"DEPCONFIG",depConfigs
        ignoreConfigs += depConfigs

    for name in recursiveListdir(os.path.join(TEST_SERVER_ROOT, "config")):
        sourcePath = os.path.join(TEST_SERVER_ROOT, "config", name)
        targetPath = os.path.join(getConfigsDir(mod), name)

        if os.path.isdir(sourcePath):
            continue

        if name in ignoreConfigs:
            print "@ Ignoring dependency config",name
            continue
        else:
            print "@ Copying config",name

        mkdirContaining(targetPath)
        shutil.copyfile(sourcePath, targetPath)

    #shutil.copytree(os.path.join(TEST_SERVER_ROOT, "config"), getConfigsDir(mod))

    return lines

"""Get all files in a directory, including subdirectories."""
def recursiveListdir(d):
    output = []
    for path, dirs, files in os.walk(d):
        # get relative path
        prefix = os.path.commonprefix((path, d))
        lastPath = path.replace(prefix, "")
        if lastPath.startswith(os.path.sep): lastPath = lastPath[1:]

        for f in files:
            output.append(os.path.join(lastPath, f))
    return output

"""Get analyzed mod content lines, possibly cached."""
def getModAnalysis(mod):
    global fn2depsfn, forceRescan

    infoFile = getInfoFilename(mod) 
    if not forceRescan and os.path.exists(infoFile):
        print "Reusing cached",getModName(mod)
        return file(infoFile).readlines()

    deps = fn2depsfn[mod]

    analyzeMod(mod, deps)

    # grab the content
    unfilteredInfo = readModInfo()

    # filter through dependencies, analyzing recursively if needed
    depsAnalyzed = []

    # everything depends on vanilla ("None"), except vanilla
    if mod is not None:
        allDeps = [None] + deps
    else:
        allDeps = deps

    for dep in allDeps:
        depsAnalyzed.append(getModAnalysis(dep))

    info = saveModInfo(mod, unfilteredInfo, depsAnalyzed, allDeps)


    return info

"""Load content into dict keyed mod name -> kind -> id -> key/value."""
def load():
    contents = {}
    for filename in os.listdir(DATA_DIR):
        if filename.startswith("."): continue

        path = os.path.join(DATA_DIR, filename)

        content = {}
        for line in file(path).readlines():
            tokens = line.replace("\n", "").split("\t")
            kind, id, key, value = tokens

            # how I miss autovivification..
            if not content.has_key(kind):
                content[kind] = {}

            if not content[kind].has_key(id):
                content[kind][id] = {}

            content[kind][id][key] = value

        contents[filename] = content

    return contents

def main():
    global fn2depsfn, forceRescan

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
        deps = getDeps(fn, info)

        for modid in getModIDs(fn, info):
            modid2fn[modid] = fn

        fn2deps[fn] = mcmodfixes.fixDeps(fn, deps)
        if len(deps) != 0:
            print fn,deps

    # build mod filename -> dependency filenames
    fn2depsfn = {None: []}
    for fn, deps in fn2deps.iteritems():
        for dep in deps:
            if not modid2fn.has_key(dep):
                print "Mod %s is missing dependency: %s. Cannot continue" % (fn, dep)
                sys.exit(-1)

            fn2depsfn[fn] = modid2fn[dep]

        fn2depsfn[fn] = [modid2fn[dep] for dep in deps if modid2fn[dep] != fn]


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
    if not os.path.exists(DATA_DIR): os.mkdir(DATA_DIR)
    if not os.path.exists(CONFIGS_DIR): os.mkdir(CONFIGS_DIR)
    vanilla = getModAnalysis(None)
    analyzedMods = {None: vanilla}

    for mod in getMods():
        getModAnalysis(mod)

if __name__ == "__main__":
    main()
