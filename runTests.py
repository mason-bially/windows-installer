'''
Created on Sep 25, 2011

@author: James Bucher
'''

#Simple script to run the tests for all packages
#a little cryptic due to windows style paths

import os
import stat


packages_folder = "packages"
folders = os.listdir(packages_folder)
for folder in folders:
    filemode = os.stat(packages_folder + "/" + folder).st_mode
    if stat.S_ISDIR(filemode) and folder != "defaultpackage":
        print "------------Running test for: " + folder + " -------------------"
        print ""
        exec "import " + packages_folder + "." + folder + "." + folder
        execstr = "foo = " + packages_folder + "." + folder + "." + folder + "." + folder + "('" + str(os.getcwd()).replace("\\", "\\\\") + "'); foo.runTest()"
        print execstr
        exec execstr
        print "------------End test for: " + folder + " -----------------------"