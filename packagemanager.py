import os

def packageLoader(name):
    try:
        return __import__("package." + name, fromlist='*')
    except ImportError, e:
        self.out.add("Could not load package: " + name + "\n\n" + "Error " + str(e.args))

class PackageManager():
    def __init__(self):
        self.packages = {}
        self.allPackNames = {}

    def LoadPackages(self, packageList = None):
        self.allPackNames = [filename for filename in os.listdir('.\\packages\\')]

        self.packages = [packageLoader(packName).__getattr__(packName)() for packName in self.allPackNames]

    def AllPackages(self):
        return self.packages
