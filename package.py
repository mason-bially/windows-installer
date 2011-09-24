# package.py Contains the class package which implements the default functions to
# Find the installed version of a program, find latest version of a program,
# Download the latest version of a program, uninstall a program and handle
# dependencies for a program.

import utils
import ConfigParser

class package:
	"""A Base class to be used as a starting point for every package
	It implements the default functions for finding the latest version
	of a program, install, uninstall etc."""
	
	def __init__(self):
		self.programName = ""
		self.url = ""
		self.regx = ""
		self.regxpos = 0
		self.downloadURL = ""
		self.downloadRegx = ""
		self.latestVersion = ""
		self.currentVersion = ""
		self.dependencies = []
		self.installed = 0
		
	def readConfig(self):
		"""Reads the configuration file
		which must be named the same as the class"""
		config = ConfigParser.RawConfigParser()
		config.read(self.__class__.__name__ + ".cfg")
		self.url = config.get('main', 'url')
		self.
		print self.url
		
	def findVersionLocal(self):
		"""Finds the local version of a program"""
		print "Sorry This appears to be a stub"
		
	def findLatestVersion(self):
		"""Finds the latest version of a program according to the web"""
		try:
			ret = scrapePage(self.regx, self.url, self.regxpos)
			self.latestVersion = ret
			return ret
		except:
			print 'unknown error running getWebVersion(%s)' % d
			raise
		else:
			return ret
	
	def install(self):
		"""Installs the latest version of a program"""
		print "Sorry This appears to be a stub"
		
	def uninstall(self):
		"""Uninstalls a program"""
		print "Sorry This appears to be a stub"
		
