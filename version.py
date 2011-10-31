import command
import packagemanager

class Command(command.BasePackageCommand):
    def __init__(self, args):
        self.runAllPackagesDefault = True
        command.BasePackageCommand.__init__(self, 
            {'prog': "version",
             'description': "Gathers and display version information for packages."})

        self.ParseArgs(args)

    def ExecutePackage(self):
        package.findLatestVersion()
        print package
            
