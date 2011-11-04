import command
import packagemanager

class Command(command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self ,
            {'prog': "fetch",
             'description': "Downloads packages."})

        self.ParseArgs(args)

    def InitArgParse(self):
        command.BasePackageCommand.InitArgParse(self)
        command.AttachDownloadArgument(self)
        
    def SortPackages(self, packages):
        packages = command.BasePackageCommand.SortPackages(self, packages)
        
        return packages
    
    def ExecutePackage(self, package):
        self.logger.debug("Starting fetch functionality")

        self.logger.info("Fetching package '"+str(package)+"'.")
        package.download(self.args['dir'])
        
        self.logger.debug("Ending fetch functionality")
