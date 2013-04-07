#!/usr/bin/python

import os
import json
import pprint

import modanalyzer

"""Given a kind, get id -> mod -> key/value. Used for showing conflicts."""
def sliceAcross(contents, kind):
    sliced = {}
    for mod, content in contents.iteritems():
        for id, data in content.get(kind, {}).iteritems():
            id = intIfInt(id)

            if not sliced.has_key(id):
                sliced[id] = {}

            sliced[id][mod] = data
    return sliced

"""Get n as an integer, if it can be parsed as an integer."""
def intIfInt(n):
    try:
        return int(n)
    except:
        return n

def getKinds(contents):
    kinds = set()
    for mod, content in contents.iteritems():
        for kind in content.keys():
            kinds.add(kind)
    return kinds

def showSlice(sliced):
    for id in sorted(sliced.keys()):
        mods = sliced[id].keys()
        print id, "\t", "\t".join(mods)

def main():
    content = modanalyzer.load()

    for kind in getKinds(content):
        print
        print "*" * (len(kind) + 4)
        print "*", kind, "*"
        print "*" * (len(kind) + 4)
        showSlice(sliceAcross(content, kind))

    #print json.dumps(content, sort_keys=True, indent=1)

if __name__ == "__main__":
    main()

