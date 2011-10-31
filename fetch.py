import command
import packagemanager

class Command(command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self ,
            {'prog': "fetch",
             'description': "Downloads packages."})

        command.AttachDownloadArgument(self)

        self.ParseArgs(args)
            
    def ExecutePackage(self, package):
        package.findLatestVersion()

        package.download(self.args['dir'])
