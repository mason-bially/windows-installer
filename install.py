import command, logging
import fetch

logger = logging.getLogger()

class Command(command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self,
            {'prog': "install",
             'description': "Installs packages."})

        self.parser.add_argument('-g', '--gui', dest="gui",
                                choices=["show", "hide", "none", "only", "last", "first"], default="hide",
                                help="Either show (ignoring quiet options) or hide (doing the best to quiet the installer) the GUI installers. Alternatively, run none of the GUI installers (skipping them) or only run the GUI installers (skipping others). Alternatively run the GUI installers first or last.")
        #self.parser.add_argument('-f', '--fetch', dest="fetch",
        #                        help="This is a quoted (' or \") string of arguments to forward to fetch specifically. Other relevent arguments will be forwarded."),
        self.parser.add_argument('--no-fetch', dest="no-fetch",
                                action='store_const', const=False,
                                help="Skip fetching the installers. Missing installers will cause errors. Will attempt to use the latest local installer version."),
        self.parser.add_argument('-d', '--download-directory', dest="dir",
                                default="downloads",
                                help="Download directory.")
        self.ParseArgs(args)
        
    def Execute(self):
        for package in self.packageManager.Packages():
            self.ExecutePackage(package)
            
    def ExecutePackage(self, package):
        global logger
        
        if not '-no-fetch' in self.argDescription:
            fetch.Command.ExecutePackage(self, package)

        package.install(not 'show' in self.args['gui'], self.args['dir'])

        
            
