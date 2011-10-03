# package.py Contains the class package which implements the default functions to
# Find the installed version of a program, find latest version of a program,
# Download the latest version of a program, uninstall a program and handle
# dependencies for a program.

from ..utils import findHighestVersion,scrapePage
import ConfigParser
import re

class Package:
	"""A Base class to be used as a starting point for every package
	It implements the default functions for finding the latest version
	of a program, install, uninstall etc."""
	
	
	#Note: packageDir is the directory that the packages folder is located
	def __init__(self, packageDir):
		self.programName = "" # Name of the program that the user sees
		self.url = "" # Main Website URL used as a last resort for searches
		self.versionRegex = "" # Regular expression that matches version
		self.versionURL = "" # URL used to find latest version used before downloadURL to find version
		self.versionRegexPos = 0
		self.downloadURL = "" #Web URL to search for file used before URL to find 
		self.downloadRegx = "" #File to search for
		self.latestVersion = "" #Latest verison online
		self.currentVersion = "" #currently installed version
		self.dependencies = [] 
		self.installed = 0
		self.readConfig(packageDir)
		self.findVersionLocal()
		self.betaOK = "" # Has a value if beta versions are acceptable
		
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
		self.findLatestVersion()
		print "Currently Installed Version is: " + self.currentVersion
		print "Latest Version is: " + self.latestVersion
		