import os
import packagemanager

class Base():
    def ParseArgs(self, args):
        curArg = ''
        curArgLen = 0
        pargs = {'': []}
        pargs.update({arg: [] for arg in self.argDescription.keys()})
        for arg in args:
            if arg[0] == '-':
                curArg = arg[1:]
                curArgLen = 0
                pargs[curArg] = []
            else:
                if curArg in self.argDescription:
                    curArgMax = self.argDescription[curArg]['maxSize']
                    if curArgMax == -1 or curArgMax > curArgLen:
                        pargs[curArg].append(arg)
                        curArgLen += 1
                    else:
                        pargs[''].append(arg)
                else:
                    pargs[curArg].append(arg)

        self.args = pargs
        
    def __init__(self, args):
        self.ParseArgs(args)

    def Execute(self):
        pass

    def PrintHelp(self):
        if 'argDescription' in self.__dict__:
            for key, option in self.argDescription.iteritems():
                print '\t', '-' + key, '\n\t  ', option['description']

class BasePackageCommand(Base):
    def __init__(self, args):
        argDescription = {'p': {'maxSize': -1, 'description':
                   "A list of packages to run this command on."}}

        if 'argDescription' in self.__dict__:
            self.argDescription.update(argDescription)
        else:
            self.argDescription = argDescription
        
        Base.__init__(self, args)

        self.packageManager = packagemanager.PackageManager()
        self.packageManager.LoadPackages(self.args['p'])

    def Execute(self):
        pass
