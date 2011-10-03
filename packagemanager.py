import sys, os

class PackageManager():
    def __init__(self):
        self.packages = {}
        self.allPackNames = {}

    def LoadPackages(self, packageList = None):
        #load packages from directory, filter for actual package directories
        self.allPackNames = [filename for filename in os.listdir('.\\packages\\')]
        self.allPackNames = filter(lambda x: x[0] == '_' and x[1] != '_', self.allPackNames)

        #debug
        print self.allPackNames

        __import__("packages", fromlist=self.allPackNames)

        for packName in self.allPackNames:
            __import__("packages." + packName, fromlist=[packName])
        
        self.packages = [getattr(getattr(sys.modules["packages." + packName], packName), packName)() for packName in self.allPackNames]

        print self.packages

    def AllPackages(self):
        return self.packages
