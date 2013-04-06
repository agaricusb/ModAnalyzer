#!/usr/bin/python

# Fixes and mod-specific data for various mods' mcmod.info files

DEP_BLACKLIST = set((
    "mod_MinecraftForge",   # we always have Forge
    "Forge", # typo for mod_MinecraftForge
    "MinecraftForge, CodeChickenCore", # typo for CodeChickenCore, broken string instead of a real list
    "Industrialcraft", # typo for IC2

    "GUI_Api", # typo for GuiAPI and not needed on server
    "EurysCore", # replaced by SlimevoidLib?
    ))


DEP_ADDITIONS = {
    "gregtech": ["IC2"],
    "MineFactoryReloaded": ["PowerCrystalsCore"],
    "NetherOres": ["PowerCrystalsCore"],
    "PowerConverters": ["PowerCrystalsCore"],
    "FlatBedrock": ["PowerCrystalsCore"],
    "immibis-microblocks": ["ImmibisCore"],
    "SlopesAndCorners": ["SlimevoidLib"],
    "ChickenChunks": ["CodeChickenCore"],
    "EnderStorage": ["CodeChickenCore"],
    "TrailMix": ["iChunUtil"],
    }

MOD_IDS = {
    "PowerCrystalsCore": ["PowerCrystalsCore"],
    }

COREMODS = [ # TODO: auto-detect
    "PowerCrystalsCore", 
    "immibis-microblocks",
    "CodeChickenCore",
    ]

FILENAME_HAS_NO_VERSION = [
    "gregtechmod.zip", # "If you are unsure about your Version, look at the "mcmod.info" inside the zip, just open it with Notepad."
    ]

REQUIRES_EXTRACTION = {
    "Millenaire": "Put in mods folder", # extracted from this folder
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

    return deps


def fixModIDs(mod, ids):
    for k, v in MOD_IDS.iteritems():
        if mod.startswith(k):
            return v 

    return ids

def isCoremod(fn):
    for k in COREMODS:
        if fn.startswith(k):
            return True
    return False 

def modNeedsRename(fn):
    for k in FILENAME_HAS_NO_VERSION:
        if fn.startswith(k):
            return True
    return False

"""Get the folder name in a mod zip which tells you to install it into the mod folders."""
def getInstructionFolder(fn):
    for k, v in REQUIRES_EXTRACTION.iteritems():
        if fn.startswith(k):
            return v
    return None

    
