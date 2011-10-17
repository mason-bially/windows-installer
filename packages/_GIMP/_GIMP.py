'''
GIMP package class

Created on Oct 16, 2011

@author: nycteaa
'''
from ..defaultpackage.package import Package



class _GIMP(Package):


    def __init__(self):
        Package.__init__(self, "\\".join(__file__.split("\\")[:-3]))
        
