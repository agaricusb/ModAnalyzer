#!/usr/bin/python

MC_VERSION = "1.5.1"
FORGE_VERSION = "7.7.1.624"

TEST_SERVER_ROOT = "test-server"

import os, urllib, zipfile, urllib2, tempfile

def setupServer():
    versionPath = MC_VERSION.replace(".", "_")
    url = "http://assets.minecraft.net/%s/minecraft_server.jar" % (versionPath,)
    mcFile = tempfile.mktemp()
    print "Retrieving %s..." % (url,)
    urllib.urlretrieve(url, mcFile)
    with zipfile.ZipFile(mcFile, 'r') as mcZip:
        print mcZip.namelist()

def main():
    if not os.path.exists(os.path.join(TEST_SERVER_ROOT, "minecraft_server.jar")):
        setupServer()

if __name__ == "__main__":
    main()
