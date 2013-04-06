#!/usr/bin/python

# Fixes for various mods' mcmod.info files

DEP_BLACKLIST = set((
    "mod_MinecraftForge",   # we always have Forge
    "Forge", # typo for mod_MinecraftForge
    "Industrialcraft", # typo for IC2

    "GUI_Api", # typo for GuiAPI and not needed on server
    ))


DEP_ADDITIONS = {
    "gregtech": ["IC2"],
    "MineFactoryReloaded": ["PowerCrystalsCore"],
    "NetherOres": ["PowerCrystalsCore"],
    "PowerConverters": ["PowerCrystalsCore"],
    "FlatBedrock": ["PowerCrystalsCore"],
    }

def getExtraDeps(mod):
    for k, v in DEP_ADDITIONS.iteritems():
        if mod.startswith(k):
            return set(v)
    return set()

def fixDeps(mod, deps):
    deps = set(deps)
    deps -= DEP_BLACKLIST
    deps |= getExtraDeps(mod)

    print "FIXDEPS:",mod,deps

    return deps

MOD_IDS = {
    "PowerCrystalsCore": ["PowerCrystalsCore"],
    }

def fixModIDs(mod, ids):
    for k, v in MOD_IDS.iteritems():
        if mod.startswith(k):
            return v 

    return ids
