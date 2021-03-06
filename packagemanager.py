import sys, os, traceback
import ourlogging

class PackageException(Exception):
    """Exception wrapping class to attach package data"""
    def __init__(self, error, inner = None, packages = None, traceback = None):
        self.inner = inner
        self.packages = packages
        self.traceback = traceback
        Exception.__init__(self, error)

    def __str__(self):
        """Prints a stack trace for the full exception we wrapped in this one"""
        if isinstance(self.packages, list):
            return Exception.__str__(self) + ": " + str(self.packages)
        elif self.inner != None and self.traceback != None:
            if self.packages != None:
                return "".join(traceback.format_tb(self.traceback)) + "\n" + Exception.__str__(self) + ": " + str(self.packages) + "\n" + str(self.inner)
            else:
                return "".join(traceback.format_tb(self.traceback)) + "\n" + Exception.__str__(self) + "\n" + str(self.inner)
        elif self.packages != None:
            return Exception.__str__(self) + ": " + str(self.packages)

class PackageManager():
    def __init__(self):
        self.packages = {}

        self.logger = ourlogging.otherLogger("Package Manager")
        
        #load all packages from directory, filter for actual package directories
        self.allPackNames = [filename for filename in os.listdir('.\\packages\\')]
        self.allPackNames = filter(lambda x: x[0] == '_' and x[1] != '_', self.allPackNames)

    def LoadAllPackages(self):
        self._loadPackages(self.allPackNames)
    
    def LoadInversePackages(self, packageList):
        self._loadPackages(list(set(self.allPackNames) - set(packageList)))

    def LoadPackages(self, packageList = []):
        if packageList == []:
            packNames = []
        else:
            #intersect of packages that are in both
            packNames = list(set(self.allPackNames) & set(packageList))

            #find packages which arn't in our list
            badPackages = list(set(packageList)-set(packNames))

            #If there are bad packages throw an exception.
            if badPackages != []:
                raise PackageException("Bad Packages", packages=badPackages)
        
        self._loadPackages(packNames)


    def _loadPackages(self, packNames):
        """This actually loads the packages, should never be called from outside this class"""
        #Most of this is black magic
        
        self.logger.debug("Importing 'packages' module.")

        #Imports the packages folder, and the symbol for each package.
        __import__("packages", fromlist=packNames)

        #Import each packag, and the class from that package.
        for packName in packNames:
            try:
                self.logger.debug("Importing 'packages."+packName+"' module.")
                __import__("packages." + packName, fromlist=[packName])
            except Exception as inner:
                raise PackageException("Package threw error during instantiation", inner, packName, sys.exc_info()[2])

        #Gets and instantiates one of each of the package classes.
        self.logger.debug("Generating package objects.")
        self.packages = [getattr(getattr(sys.modules["packages." + packName], packName), packName)() for packName in packNames]

    def Packages(self):
        return self.packages
