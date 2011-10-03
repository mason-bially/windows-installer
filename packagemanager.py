import sys, os

class PackageManager():
    def __init__(self):
        self.packages = {}
        self.allPackNames = {}

    def LoadPackages(self, packageList = None):
        #load packages from directory, filter for actual package directories, this could be gloablized
        self.allPackNames = [filename for filename in os.listdir('.\\packages\\')]
        self.allPackNames = filter(lambda x: x[0] == '_' and x[1] != '_', self.allPackNames)

        if packageList != None:
            #intersect of packages that are in both
            packNames = list(set(self.allPackNames) & set(packageList))

            #print errorsof the difference
            badPackages = list(set(packageList)-set(packNames))

            if badPackages != []:
                print "Bad Packages:", badPackages
                return
        else:
            packNames = self.allPackNames

        __import__("packages", fromlist=packNames)

        for packName in packNames:
            __import__("packages." + packName, fromlist=[packName])
        
        self.packages = [getattr(getattr(sys.modules["packages." + packName], packName), packName)() for packName in packNames]

    def AllPackages(self):
        return self.packages
