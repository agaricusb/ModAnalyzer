#!/usr/bin/python

import os
import json
import pprint

DATA_DIR = "data"

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
    content = load()

    print json.dumps(content, sort_keys=True, indent=1)

if __name__ == "__main__":
    main()

