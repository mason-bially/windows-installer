import command
import packagemanager

class Command(command.AttachNoScrape, command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self, 
            {'prog': "version",
             'description': "Gathers and display version information for packages."})
        self.InitInvertAllPackages()
        
        self.ParseArgs(args)

    def ExecutePackage(self, package):
        version = package.versionInformation()
        for (k, v) in version.items():
            if v == "":
                version[k] = '[Empty]'
        self.logger.info(package.name() + "\n\tCurrent: " + version['current'] + "\n\tLatest:  " + version['latest'])
            
