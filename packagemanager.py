import sys, os

class PackageManager():
    def __init__(self):
        self.packages = {}
        self.allPackNames = {}

    def LoadPackages(self, packageList = None):
        self.allPackNames = [filename for filename in os.listdir('.\\packages\\')]
        self.allPackNames.remove("defaultpackage")
        self.allPackNames = filter(lambda x: x[-3:] != '.py' and x[-4:] != '.pyc' , self.allPackNames)

        print self.allPackNames

        for packName in self.allPackNames:
            __import__("packages." + packName, fromlist=[packName])
        
        self.packages = [getattr(getattr(sys.modules["packages." + packName], packName), packName)() for packName in self.allPackNames]

        print self.packages

    def AllPackages(self):
        return self.packages
