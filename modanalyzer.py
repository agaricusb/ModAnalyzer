#!/usr/bin/python

MC_VERSION = "1.5.1"
FORGE_VERSION = "7.7.1.624"

TEST_SERVER_ROOT = "test-server"

import os, urllib, zipfile, urllib2, tempfile

def setupServer():
    mcZip = getURLZip("http://assets.minecraft.net/%s/minecraft_server.jar" % (MC_VERSION.replace(".", "_"),))
    print mcZip.namelist()
    
    forgeZip = getURLZip("http://files.minecraftforge.net/minecraftforge/minecraftforge-universal-%s-%s.zip" % (MC_VERSION, FORGE_VERSION))
    print forgeZip.namelist()

def getURLZip(url):
    f = tempfile.mktemp()
    print "Retrieving %s..." % (url,)
    urllib.urlretrieve(url, f)
    return zipfile.ZipFile(f, 'r')


def main():
    if not os.path.exists(os.path.join(TEST_SERVER_ROOT, "minecraft_server.jar")):
        setupServer()

if __name__ == "__main__":
    main()
