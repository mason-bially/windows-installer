'''
Created on Oct 18, 2011

@author: levienk
'''
from ..defaultpackage.package import Package



class _ImageMagick(Package):


    def __init__(self):
        Package.__init__(self)
        
    def findLatestVersion(self):
        version = Package.findLatestVersion(self)
        version = self.latestVersion.replace(' ', '.')
        self.latestVersion = version
        return version
