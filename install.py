import command, logging
import fetch

class Functionality(command.Base, fetch.Functionality):
    def ExecutePackage(self, package):
        self.logger.debug("Starting install functionality")
        
        if not self.args['no-fetch']:
            fetch.Functionality.ExecutePackage(self, package)

        self.logger.info("Installing package.")
        package.install(not 'show' in self.args['gui'], self.args['dir'])
        
        self.logger.debug("Ending install functionality")


class Command(command.BasePackageCommand, Functionality):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self,
            {'prog': "install",
             'description': "Installs packages."})

        self.parser.add_argument('-g', '--gui', dest="gui",
                                choices=["show", "hide", "none", "only", "last", "first"], default="hide",
                                help="Either show (ignoring quiet options) or hide (doing the best to quiet the installer) the GUI installers. Alternatively, run none of the GUI installers (skipping them) or only run the GUI installers (skipping others). Alternatively run the GUI installers first or last.")
        self.parser.add_argument('--no-fetch', dest="no-fetch",
                                action='store_true',
                                help="Skip fetching the installers. Missing installers will cause errors. Will attempt to use the latest local installer version."),
        command.AttachDownloadArgument(self)
        
        self.ParseArgs(args)
        self.PostArgInit()

        
            
