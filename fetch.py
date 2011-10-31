import command
import packagemanager

class Functionality(command.Base):
    def ExecutePackage(self, package):
        self.logger.debug("Starting fetch functionality")

        self.logger.info("Fetching package '"+str(package)+"'.")
        package.download(self.args['dir'])
        
        self.logger.debug("Ending fetch functionality")


class Command(command.BasePackageCommand, Functionality):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self ,
            {'prog': "fetch",
             'description': "Downloads packages."})

        command.AttachDownloadArgument(self)

        self.ParseArgs(args)
        self.PostArgInit()

