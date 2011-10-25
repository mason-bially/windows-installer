# package.py Contains the class package which implements the default functions to
# Find the installed version of a program, find latest version of a program,
# Download the latest version of a program, uninstall a program and handle
# dependencies for a program.

from ..utils import findHighestVersion,scrapePage,parsePage,downloadFile
import ConfigParser, logging

import re, os
from subprocess import call
from BeautifulSoup import BeautifulSoup
class InstallError(Exception):
    
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    

logger = logging.getLogger(__name__)

packageDir = "\\".join(__file__.split("\\")[:-3])

class Package:
    """A Base class to be used as a starting point for every package
    It implements the default functions for finding the latest version
    of a program, install, uninstall etc."""
    
    #Note: packageDir is the directory that the packages folder is located
    def __init__(self):
        self.programName = "" # Name of the program that the user sees
        self.arch = "" # 32bit or 64bit specified as x86 or x86_64
        self.url = "" # Main Website URL used as a last resort for searches
        self.versionRegex = "" # Regular expression that matches version
        self.versionURL = "" # URL used to find latest version used before downloadURL to find version
        #self.versionRegexPos = 0
        self.downloadURL = "" #Web URL to search for file used before URL to find 
        self.downloadRegex = "" #File to search for
        self.downloadLink = "" #To be used if a download link can be formed with just program Version
        self.downloadedPath = ""
        self.linkRegex = "" #To be used with Beautiful Soup to scan a page for probable download links if above fails
        self.latestVersion = "" #Latest verison online
        self.currentVersion = "" #currently installed version
        self.dependencies = []
        self.installMethod = "" # Installation method exe, msi, or zip
        self.installSilentArgs = "" # Arguments to pass to installer for silent install
        self.installed = False
        self.uninstalled = False
        self.readConfig()
        self.findVersionLocal()
        self.betaOK = "" # Has a value if beta versions are acceptable
        self.regVenderName = ""
        self.regProgName = ""
        self.regVersLocations = ['''SOFTWARE\Wow6432Node''',
                                '''SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall''']
        
    def readConfig(self):
        """Reads the configuration file
        which must be named the same as the class"""
        global packageDir
        # The config path is necessary to find the config file
        # because the cwd could change and we need to know where the module is located
        config = ConfigParser.RawConfigParser()
        packageDir = packageDir.rstrip("\\") #clean input just in case
        configpath = str(self.__class__).rstrip(self.__class__.__name__).rstrip(".")
        configpath = packageDir + "\\" + configpath.replace(".", "\\") + ".cfg"
        config.read(configpath)
        if configpath == []:
            raise ConfigParser.Error("Config File could not be read path was: " + configpath)
        # Note One cannot itearate over a dict
        # and change its contents. Thus the following
        names = []
        for name in self.__dict__:
            names.append(name)
        for name in names:
            try:
                self.__dict__[name] = config.get('main', name)
            except ConfigParser.NoOptionError as NoOption:
                print "Error Reading config for: " + self.__class__.__name__ + ": " + str(NoOption)
        
    def findVersionLocal(self):
        """Finds the local version of a program online.
        Uses self.versionRegex to match all versions on self.versionURL"""
        self.currentVersion="INVLAID_VERSION"
        
    def findLatestVersion(self):
        """Attempts to find the latest version of a page """
        try:
            url = ""
            regex = self.versionRegex
            # Determine What URL to use
            # Try using most accurate URL first
            if self.versionURL != "":
                url = self.versionURL
            elif self.downloadURL != "":
                url = self.downloadURL
            elif self.url != "":
                url = self.url
            versions = scrapePage(regex, url)
            if self.betaOK == "":
                versionsTemp = []
                for version in versions:
                    if re.search("beta",version) == None:
                        versionsTemp.append(version)
                versions = versionsTemp
            # Filter out blanks
            versions = filter(lambda a: a != '', versions)
            ret = findHighestVersion(versions)
            self.latestVersion = ret
            return ret
        except:
            print 'unknown error running getWebVersion()'
            raise
        else:
            return ret
    
    def download(self, directory):
        """Downloads the latest version of a program"""
        #TODO: Make this handle download errors gracefully
        
        #Check to see if findLatestVersion has been run
        if self.latestVersion == "":
            self.findLatestVersion()
        #Check to see if file is already downloaded
        for packageFile in os.listdir(directory):
            filename = self.__class__.__name__ + "-" + self.latestVersion
            if packageFile.rfind(filename) != -1:
                self.downloadedPath = directory + '/' + filename + '.' + packageFile.split(".")[-1]
                break
        #Dont redownload File if already downloaded
        if self.downloadedPath != "":
            return self.downloadedPath
        
        #Otherwise Download file
        if self.downloadLink != '':
            self.downloadLink = self.parseVersionSyntax(self.downloadLink)
            fileURL = self.downloadLink
        elif self.downloadRegex != '':
            self.downloadRegex = self.parseDownloadRegex()
            fileURL = scrapePage(self.downloadRegex, self.downloadURL)[0]
        else:
            fileURL = parsePage(self.linkRegex, self.downloadURL)
        if not re.match(".*:.*", fileURL):
            # If the path is not absolute we need to put the downloadURL on the front
            temp = self.downloadURL.split('/')[-1] # Find the last bit of downloadURL
            temp = self.downloadURL.rstrip(temp) # strip of everything up to /
            fileURL = temp + fileURL
        fileName = self.__class__.__name__ + "-" + self.latestVersion
        self.downloadedPath = downloadFile(fileURL, directory, fileName)
        return self.downloadedPath

    def install(self, quiet=False, downloadPath=""):
        """Installs the latest version of a program"""
        #TODO: add check to see if file is downloaded. If not download it
        if self.downloadedPath == "":
            self.download(downloadPath)
        
        #Attempt to auto figure out Install method using path
        if self.installMethod == "":
            self.installMethod = self.downloadedPath.split(".")[-1].lower()
            
        #Call correct installation method
        if self.installMethod == "exe":
            self.installExe()
        elif self.installMethod == "msi":
            self.installMsi()
        elif self.installMethod == "zip":
            self.installZip()
        else:
            raise InstallError("Installation Method Not supported")
        
    def uninstall(self):
        """Uninstalls a program"""
        print "Sorry This appears to be a stub"
        
    def __str__(self):
        prettyStr = "Package Name: " + self.__class__.__name__ + '\n'
        prettyStr += "Program Name: " + self.programName
        prettyStr += "Program Version Latest: " + self.latestVersion + "\n"
        prettyStr += "Program Version Installed: " + self.currentVersion + "\n"
        return prettyStr

    def parseVersionSyntax(self, string):
        """Takes in a string an looks for #VERSION# and #DOTLESSVERSION# and deals with it"""
        #TODO: Fix this, doesn't actually parse it just replaces currently
        # As such this function is a major hack!
        
        #Error Checking
        if self.latestVersion == "":
            self.findLatestVersion()
        
        if (string.find("#VERSION#") != -1):
            string = string.replace("#VERSION#", self.latestVersion)
        if (string.find("#VERSIONFIRST#") != -1):
            string = string.replace("#VERSIONFIRST#", self.latestVersion.split('.')[0])
        if (string.find("#DOTLESSVERSION#") != -1):
            string = string.replace('#DOTLESSVERSION#', self.latestVersion.replace('.',''))
        return string
    
    def parseDownloadRegex(self):
        """Takes in the filename specified in a package config and gets rid of #VERSION#"""
        self.downloadRegex = self.parseVersionSyntax(self.downloadRegex)
        return self.downloadRegex
    
    def runTest(self):
        self.findLatestVersion()
        self.download("""C:/Users/James Bucher/Downloads/Download-Test/""")
        print "Currently Installed Version is: " + self.currentVersion
        print "Latest Version is: " + self.latestVersion
    
    def installFork(self, quiet=False, downloadPath=""):
        #TODO: Add check to see if file is already even if the downloadedPath is null
        #This should search the download path for package downloads 
        if self.downloadedPath == "":
            raise InstallError("Error no installation file downloaded")
        #Change install arguments from a string to a list
        exec "self.installSilentArgs = " + self.installSilentArgs
        #Launch the installer with 
        call([self.downloadedPath].append(self.installSilentArgs))
    
    def installExe(self, quiet=False, downloadPath=""):
        self.installFork(quiet, downloadPath)
    
    def installMsi(self, quiet=False, downloadPath=""):
        self.downloadedPath = self.downloadedPath.replace("/","\\");
        args = ["msiexec", "/qb", "/i", self.downloadedPath]
        call(args)
    
    def installZip(self, quiet=False, downloadPath=""):
        print "This appears to be a stub"
