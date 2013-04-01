#!/usr/bin/python

MC_VERSION = "1.5.1"
FORGE_VERSION = "7.7.1.624"

TEST_SERVER_ROOT = "temp-server"
TEST_SERVER_FILE = "minecraft_server+forge.jar"

import os, urllib, zipfile, urllib2, tempfile

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
    print "Server at",serverFilename

def getURLZip(url):
    f = tempfile.mktemp()
    print "Retrieving %s..." % (url,)
    urllib.urlretrieve(url, f)
    return zipfile.ZipFile(f, 'r')


def main():
    server = os.path.join(TEST_SERVER_ROOT, TEST_SERVER_FILE)
    if not os.path.exists(server):
        if not os.path.exists(TEST_SERVER_ROOT):
            os.mkdir(TEST_SERVER_ROOT)

        setupServer(server)

if __name__ == "__main__":
    main()
