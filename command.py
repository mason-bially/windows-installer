import os
import packagemanager

class Base():
    def __init__(self, args):
        self.args = args

    def Execute(self):
        pass

class BasePackageCommand(Base):
    def __init__(self, args):
        Base.__init__(self, args)
        self.packages = args

        self.packageManager = packagemanager.PackageManager()
        self.packageManager.LoadPackages()
