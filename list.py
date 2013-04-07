#!/usr/bin/python

import os
import json
import pprint

DATA_DIR = "data"

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
    content = load()

    for kind in getKinds(content):
        print
        print "*" * (len(kind) + 4)
        print "*", kind, "*"
        print "*" * (len(kind) + 4)
        showSlice(sliceAcross(content, kind))

    #print json.dumps(content, sort_keys=True, indent=1)

if __name__ == "__main__":
    main()

