ModAnalyzer - a tool for analyzing Minecraft mods and resolving conflicts

Got a bunch of mods you want to use together, but you keep getting ID conflicts? 
Want to know what content is in a mod before installing it, or browse the available
mods for the kind of content you're looking for? ModAnalyzer might be able to help.

ModAnalyze is split into several parts:

* a Minecraft mod to load along with the mods you want to analyze
* a driver script modanalyzer.py to mass analyze mods and filter the results
* a utility script modlist.py to view a summary of the analysis results by ID
* finally, modresolve.py to install the mods and automatically edit configs to resolve conflicts

Usage:

1. download a ton of mods, and place them in the "allmods" folder
2. run modanalyze.py and it should setup a test server and analyze each mod, placing gathered results in "data" and "configs"
3. run modresolve.py to configure a test server with all the mods installed in "temp-server"

Conflict resolution is not 100%, since some mods configuration is not easily programmatically configurable (or at all).

The script will show you what IDs could not be changed, and you can edit them manually. Copy the contents of "temp-server"
to your real server, make the edits, then copy the same contents to the client, making any needed changes or additions.

If there are too many irresolvable conflicts, you can edit "priority.txt" and reorder the mods, higher first,
to take precedence when choosing which mod to move. By default, mods with more content will have higher priority.
Note that re-running modresolve.py will erase the mods and configs in "temp-server", regenerating from scratch.

Examples:

* [AAConfigPack](https://github.com/agaricusb/AAConfigPack) - generated with ModAnalyze (few manual changes), 83 mods on Minecraft 1.5.1

Released as open source under the BSD license, redistribution, changes, forks, pull requests, etc. welcome.

