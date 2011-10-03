import os
import packagemanager

class Base():
    def ParseArgs(self, args):
        self.args = args

        curArg = None
        pargs = {}
        for arg in self.args:
            if arg[0] == '-':
                curArg = arg
                pargs[curArg] = []
            else:
                pargs[curArg].append(arg)

        self.pargs = pargs
        self.lastArg = curArg

        print self.__dict__['pargs']
        
    def __init__(self, args):
        self.ParseArgs(args)

    def Execute(self):
        pass

class BasePackageCommand(Base):
    def ParseArgs(self, args):
        Base.ParseArgs(self, args)

        self.packages = self.pargs[self.lastArg][1:]
    
    def __init__(self, args):
        Base.__init__(self, args)

        self.packageManager = packagemanager.PackageManager()
        self.packageManager.LoadPackages(self.packages)

    def Execute(self):
        pass
