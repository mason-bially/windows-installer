# package.py Contains the class package which implements the default functions to
# Find the installed version of a program, find latest version of a program,
# Download the latest version of a program, uninstall a program and handle
# dependencies for a program.

from ..utils import findHighestVersion,scrapePage,parsePage,downloadFile
import ConfigParser, ourlogging

import re, os
from subprocess import call
import zipfile
import shutil

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
        self.arch = "" # 32bit or 64bit or both specified as x86 or x86_64 or both
                       # Note: Both is for installers like virtualbox that work for both arch and auto select
        self.url = "" # Main Website URL used as a last resort for searches
        self.versionRegex = "" # Regular expression that matches version
        self.versionURL = "" # URL used to find latest version used before downloadURL to find version
        self.downloadURL = "" #Web URL to search for file used before URL to find 
        self.downloadRegex = "" #File to search for
        self.downloadLink = "" #To be used if a download link can be formed with just program Version
        self.linkRegex = "" #To be used with Beautiful Soup to scan a page for probable download links if above fails
        self.dependencies = [] #Software that the program Has to have to run
                               #Note: for dependencies that have options such as the Java Runtime Environment or Java Development kit
                               #This can contain lists of lists: [["JDK", "JRE"] "FOO"]. This means that either the JDK or JRE are
                               #Required but either will work and that the package FOO is required
        self.recommended = [] #Software that the program runs better with (ex: camstudio and camstudio codecs)
        self.installMethod = "" # Installation method exe, msi, or zip
        self.installSilentArgs = "" # Arguments to pass to installer for silent install
        self.betaOK = "" # Has a value if beta versions are acceptable
        self.regVenderName = "" #Name of the vendor in the registry
        self.regProgName = "" #Name of the program in the registry (defaults to programName)
        self.regVersLocations = ['''SOFTWARE\Wow6432Node''',
                                '''SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall''']
        self.installDir = "" #Directory that files should be installed to auto fills in "Program Files" or "Program Files (x86)" 
        ### LEAVE THIS LAST ###
        self.readConfig(logger) 
        ### END CONFIG ###

        #These values are not read from the config file
        self.logger = logger
        self.currentVersion = "" #Currently installed version
        self.latestVersion = "" #Latest verison online
        self.downloadedPath = "" #Path installer was downloaded to
        self.actualURL = "" #Actual URL that was downloaded (after redirects)
        self.installed = False
        self.uninstalled = False

        #Default logic to find the correct Program Files Directory
        #TODO: add logic to pull this from package name
        if (self.installDir == "") and (self.arch.find("64") > -1):
            self.installDir = "C:\\Program Files"
        elif (self.installDir == "") and ((self.arch.find("32") > -1) or (self.arch.find("86") > -1)):
            self.installDir = "C:\\Program Files (x86)"
        else:
            self.logger.debug("Arch could not be determined defaulting installDir to C:\\Program Files")
            self.installDir = "C:\\Program Files"

        #Get the dependencies as a list
        if self.dependencies != []:
            exec "self.dependencies = " + self.dependencies
        
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
            raise #PackageError('unknown error running getWebVersion()')
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
            self.linkRegex = self.parseVersionSyntax(self.linkRegex)
            self.downloadURL = self.parseVersionSyntax(self.downloadURL)
            fileURL = parsePage(self.linkRegex, self.downloadURL)
        if not re.match(".*:.*", fileURL):
            #TODO: Fix this - It doesn't cover the case where the link is /foo/bar
            #Which should become: http://website.com/foo/bar
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
        downloadedFilePath = downloadFile(fileURL, directory, fileName)['downloadedPath']
        self.logger.debug("Finished downloading file to '" + downloadedFilePath + "'")
        return downloadedFilePath


    def install(self, hideGui=True, downloadPath=""):
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
        self.logger.critical("uninstall not implemented")

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
        """Runs a self diagnostic on the package. Note: this is basically depricated"""
        #TODO: Check to be sure we can remove this. All functionality provied by this should be accessable
        #via the command line.
        self.findLatestVersion()
        self.download("""C:/Users/James Bucher/Downloads/Download-Test/""")
        print "Currently Installed Version is: " + self.currentVersion
        print "Latest Version is: " + self.latestVersion
    
    def installFork(self, quiet=True, downloadPath=""):
        #TODO: Merge this into installExe
        if self.downloadedPath == "":
            raise PackageError("Error no installation file downloaded")
        #Change install arguments from a string to a list
        self.downloadedPath = self.downloadedPath.replace("/","\\");
        args=[self.downloadedPath]
        if quiet and self.installSilentArgs != "":
            exec "self.installSilentArgs = " + self.installSilentArgs
            args += self.installSilentArgs
        #Launch the installer
        if call(args) != 0:
            raise PackageError("Package Installation Failed")

    
    def installExe(self, quiet=True, downloadPath=""):
        self.logger.debug("Attempting exe installation")
        self.installFork(quiet, downloadPath)
        self.logger.debug("Finished exe installation")
    
    def installMsi(self, quiet=True, downloadPath=""):
        if self.downloadedPath == "":
            raise PackageError("Error no installation file downloaded")
        self.downloadedPath = self.downloadedPath.replace("/","\\");
        if quiet:
            args = ["msiexec", "/qb", "/i", self.downloadedPath]
        else:
            args = [self.downloadedPath]
        self.logger.debug("Attempting MSI installation")
        if call(args) != 0:
            raise PackageError("Package Installation Failed")
        self.logger.debug("Finished MSI installation")
    
    def installZip(self, quiet=False, downloadPath=""):
        #TODO: add logic to determine arch via files from zip file
        self.logger.debug("Attempting ZIP installation")
        if self.downloadedPath == "":
            self.logger.critical("ERROR NO INSTALLATION FILE DOWNLOADED")
            raise PackageError("Error no installation file downloaded")
        self.downloadedPath = self.downloadedPath.replace("/","\\");
        #Open Zip File that was downloaded
        with zipfile.ZipFile(self.downloadedPath, 'r') as installFile:
            #Check to see if extraction DIR exists if so delete it
            if os.path.exists(downloadPath + "/" + self.programName + "-" + self.latestVersion):
                self.logger.debug("Removing already extracted files from download directory")
                shutil.rmtree(downloadPath + "/" + self.programName + "-" + self.latestVersion)
            #Extract files to a temp DIR
            self.logger.debug("Extracting zip file for install")
            installFile.extractall(downloadPath + "/" + self.programName + "-" + self.latestVersion)
            #Find subdir in extracted path that actually contains the files we want
            #For example: if a zip file exracts to foo/bar.exe we don't want to have
            #Our program become c:/program File/Program/foo/bar.exe we want it to be
            #c:/program files/program/bar.exe
            iterdir = downloadPath + "/" + self.programName + "-" + self.latestVersion
            folder = len(os.listdir(iterdir))
            while folder == 1:
                iterdir = iterdir + "/" + os.listdir(iterdir)[0]
                folder = len(os.listdir(iterdir))
            if folder <= 0:
                self.logger.critical("Error Zip File was empty")
            self.logger.debug("Moving extracted files to: " + self.installDir + "\\" + self.programName)
            shutil.move(iterdir, self.installDir +"\\" + self.programName)
            self.logger.debug("Removing extra filder generated by extraction")
            shutil.rmtree(downloadPath + "/" + self.programName + "-" + self.latestVersion)

    def canHideGui(self):
        """True if the gui is hideable, false otherwise"""
        return not self.installSilentArgs == ""
    def determineArch(self):
        """Sets self.Arch by using the downloadURL or downloaded files contents"""
        #TODO: Fill in this function
        self.logger.debug("determineArch not implemented yet")
