# package.py Contains the class package which implements the default functions to
# Find the installed version of a program, find latest version of a program,
# Download the latest version of a program, uninstall a program and handle
# dependencies for a program.

from ..utils import findHighestVersion,scrapePage,parsePage,downloadFile
import ConfigParser, ourlogging

import re, os
from subprocess import call
from BeautifulSoup import BeautifulSoup
class PackageError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


packageDir = "\\".join(__file__.split("\\")[:-3])

class Package:
    """A Base class to be used as a starting point for every package
    It implements the default functions for finding the latest version
    of a program, install, uninstall etc."""
    
    #Note: packageDir is the directory that the packages folder is located
    def __init__(self):
        logger = ourlogging.packageLogger(self.name())

        ### CONFIG ###
        # These are values which may appear in a config File
        self.programName = "" # Name of the program that the user sees
        self.arch = "" # 32bit or 64bit specified as x86 or x86_64
        self.url = "" # Main Website URL used as a last resort for searches
        self.versionRegex = "" # Regular expression that matches version
        self.versionURL = "" # URL used to find latest version used before downloadURL to find version
        self.downloadURL = "" #Web URL to search for file used before URL to find 
        self.downloadRegex = "" #File to search for
        self.downloadLink = "" #To be used if a download link can be formed with just program Version
        self.linkRegex = "" #To be used with Beautiful Soup to scan a page for probable download links if above fails
        self.dependencies = []
        self.installMethod = "" # Installation method exe, msi, or zip
        self.installSilentArgs = "" # Arguments to pass to installer for silent install
        self.betaOK = "" # Has a value if beta versions are acceptable
        self.regVenderName = ""
        self.regProgName = ""
        self.regVersLocations = ['''SOFTWARE\Wow6432Node''',
                                '''SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall''']
        
        ### LEAVE THIS LAST ###
        self.readConfig(logger) 
        ### END CONFIG ###
        
        self.logger = logger
        self.currentVersion = ""
        self.latestVersion = "" #Latest verison online
        self.downloadedPath = ""
        self.installed = False
        self.uninstalled = False
        
    def readConfig(self,logger):
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
            raise PackageError("Config File could not be read; path was: " + configpath)
        
        # Note One cannot itearate over a dict
        # and change its contents. Thus the following
        names = []
        for name in self.__dict__:
            names.append(name)
        for name in names:
            try:
                self.__dict__[name] = config.get('main', name)
            except ConfigParser.NoOptionError as NoOption:
                logger.debug("Config read error: " + str(NoOption))
        
    def findLocalVersion(self):
        """Finds the local version of a program online.
        Uses self.versionRegex to match all versions on self.versionURL"""
        self.currentVersion="Not Implemented"
        
    def findLatestVersion(self):
        """Attempts to find the latest version of a page """
        self.logger.debug("Finding latest web version")
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
            raise PackageError('unknown error running getWebVersion()')
        else:
            return ret

    def fileName(self):
        return self.__class__.__name__ + "-" + self.latestVersion
    
    def fileNameWithoutVersion(self):
        return self.__class__.__name__ + "-"
    
    def findFile(self, directory):
        """Returns true and updates downloadFile if a file belonging to us in the directory exists."""
        self.logger.debug("Checking for a downloaded file.")
        
        #Don't bother looking if we already know where one is.
        if self.downloadedPath != "" and self.downloadedPath.find(directory) != -1:
            return True
        
        #Enumerate files, see if ours is there.
        for packageFile in os.listdir(directory):
            filename = self.fileNameWithoutVersion()
            if packageFile.rfind(filename) != -1:
                self.downloadedPath = directory + '/' + packageFile
                return True
        return False

    def findLatestFile(self, directory):
        """Returns true and updates downloadFile if a file belonging to us in the directory exists."""
        self.logger.debug("Checking for latest downloaded file.")

        if self.latestVersion == "":
            raise PackageError("Not enough information to determine latest downloaded file. Missing latest version.")
        
        #Enumerate files, see if ours is there.
        for packageFile in os.listdir(directory):
            filename = self.fileName()
            if packageFile.rfind(filename) != -1:
                self.downloadedPath = directory + '/' + packageFile
                return True
        return False

    def determineFileURL(self):
        """Helper function to determine the download url"""
        self.logger.debug("Determining download fileURL.")
        if self.downloadLink != '':
            self.downloadLink = self.parseVersionSyntax(self.downloadLink)
            fileURL = self.downloadLink
        elif self.downloadRegex != '':
            self.downloadRegex = self.parseDownloadRegex()
            fileURL = scrapePage(self.downloadRegex, self.downloadURL)[0]
        else:
            fileURL = parsePage(self.linkRegex, self.downloadURL)
        if not re.match(".*:.*", fileURL):
            self.logger.debug("Adjusting unabsolute path")
            # If the path is not absolute we need to put the downloadURL on the front
            temp = self.downloadURL.split('/')[-1] # Find the last bit of downloadURL
            temp = self.downloadURL.rstrip(temp) # strip of everything up to /
            fileURL = temp + fileURL

        return fileURL
    
    def download(self, directory):
        """Downloads the latest version of a program to directory"""
        
        if self.findLatestFile(directory):
            self.logger.debug("File found in cache.")
            return self.downloadedPath

        #Otherwise Download file
        fileURL = self.determineFileURL()
        fileName = self.fileName()

        self.logger.debug("Attempting to download file from '" + fileURL + "' as: '" + fileName + "'")
        downloadedFilePath = downloadFile(fileURL, directory, fileName)
        self.logger.debug("Finished downloading file to '" + downloadedFilePath + "'")
        return downloadedFilePath


    def install(self, hideGui=False, downloadPath=""):
        """Installs the downloaded version of a program from downloadPath"""
    
        #Check to see if the needed file is already downloaded. Error otherwise.
        if not self.findFile(downloadPath):
            raise PackageError("No downloaded package to install with.")
        
        #Attempt to auto figure out Install method using path
        if self.installMethod == "":
            self.installMethod = self.downloadedPath.split(".")[-1].lower()
            self.logger.debug("Discovered installation method: " + self.installMethod)
            
        #Call correct installation method
        if self.installMethod == "exe":
            self.installExe(hideGui, downloadPath)
        elif self.installMethod == "msi":
            self.installMsi(hideGui, downloadPath)
        elif self.installMethod == "zip":
            self.installZip(hideGui, downloadPath)
        else:
            raise PackageError("Installation Method Not supported")

       
    def uninstall(self):
        """Uninstalls a program"""
        self.logger.critical("Uninstall not implemented")

    def name(self):
        return self.__class__.__name__[1:]
    
    def __str__(self):
        return self.programName

    def versionInformation(self):
        return {'current': self.currentVersion,
                'latest': self.latestVersion}

    def parseVersionSyntax(self, string):
        """Takes in a string an looks for #VERSION# and #DOTLESSVERSION# and deals with it"""
        #TODO: Fix this, doesn't actually parse it just replaces currently
        # As such this function is a major hack!
        
        #Error Checking
        if self.latestVersion == "":
             raise PackageError("Not enough information to complete file replacement. Missing latest version.")
        
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
            raise PackageError("Error no installation file downloaded")
        #Change install arguments from a string to a list
        exec "self.installSilentArgs = " + self.installSilentArgs
        #Launch the installer with 
        call([self.downloadedPath].append(self.installSilentArgs))
    
    def installExe(self, quiet=False, downloadPath=""):
        self.logger.debug("Attempting exe installation")
        self.installFork(quiet, downloadPath)
        self.logger.debug("Finished exe installation")
    
    def installMsi(self, quiet=False, downloadPath=""):
        self.downloadedPath = self.downloadedPath.replace("/","\\");
        args = ["msiexec", "/qb", "/i", self.downloadedPath]
        self.logger.debug("Attempting MSI installation")
        call(args)
        self.logger.debug("Finished MSI installation")
    
    def installZip(self, quiet=False, downloadPath=""):
        print "This appears to be a stub"

    def canHideGui(self):
        """True if the gui is hideable, false otherwise"""
        return not self.installSilentArgs == ""

