# package.py Contains the class package which implements the default functions to
# Find the installed version of a program, find latest version of a program,
# Download the latest version of a program, uninstall a program and handle
# dependencies for a program.

import utils
import ConfigParser

class Package:
	"""A Base class to be used as a starting point for every package
	It implements the default functions for finding the latest version
	of a program, install, uninstall etc."""
	
	
	#Note: packageDir is the directory that the packages folder is located
	def __init__(self, packageDir):
		self.programName = ""
		self.url = ""
		self.versionRegex = ""
		self.versionURL = ""
		self.versionRegexPos = 0
		self.downloadURL = "" #Web Dir to search for file
		self.downloadRegx = "" #File to search for
		self.latestVersion = "" #Latest verison online
		self.currentVersion = "" #currently installed version
		self.dependencies = []
		self.installed = 0
		self.readConfig(packageDir)
		self.findVersionLocal()
		
	def readConfig(self, packageDir):
		"""Reads the configuration file
		which must be named the same as the class"""
		# The config path is necessary to find the config file
		# because the cwd could change and we need to know where the module is located
		config = ConfigParser.RawConfigParser()
		packageDir = packageDir.rstrip("\\") #clean input just in case
		configpath = str(self.__class__).rstrip(self.__class__.__name__).rstrip(".")
		configpath = packageDir + "\\" + configpath.replace(".", "\\") + ".cfg"
		config.read(configpath)
		if configpath == []:
			raise ConfigParser.Error("Config File could not be read path was: " + configpath)
		try:
			self.url = config.get('main', 'url')
			self.programName = config.get('main', 'programName')
			self.regex = config.get('main', 'regex')
		except ConfigParser.NoOptionError as NoOption:
			print "Error Reading config for " + self.__class__.__name__ + ": " + str(NoOption)
			raise
		
	def findVersionLocal(self):
		"""Finds the local version of a program online.
		Uses self.versionRegex to match all versions on self.versionURL"""
		self.currentVersion="INVLAID_VERSION"
		
	def findLatestVersion(self):
		"""Attempts to find the latest version of a page """
		
		try:
			ret = utils.scrapePage(self.regx, self.url, self.regxpos)
			self.latestVersion = ret
			return ret
		except:
			print 'unknown error running getWebVersion()'
			raise
		else:
			return ret
	def download(self):
		"""Downloads the latest version of a program"""
		print "Sorry this appears to be a stub"
	def install(self, quiet):
		"""Installs the latest version of a program"""
		print "Sorry This appears to be a stub"
		
	def uninstall(self):
		"""Uninstalls a program"""
		print "Sorry This appears to be a stub"
		
	def __str__(self):
		prettyStr = "Package Name: " + self.__class__.__name__ + '\n'
		prettyStr += "Program Name: " + self.programName
		prettyStr += "Program Version Latest: " + self.latestVersion + "\n"
		prettyStr += "Program Version Installed: " + self.currentVersion + "\n"
		return prettyStr
	
	def runTest(self):
		print "Currently Installed Version is: " + self.currentVersion
		print "Latest Version is: " + self.latestVersion
		