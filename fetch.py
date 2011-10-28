import command
import packagemanager

class Command(command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self ,
            {'prog': "fetch",
             'description': "Downloads packages."})

        self.parser.add_argument('-d', '--download-directory', dest="dir",
                                default="downloads",
                                help="Directory to download files to.")

        self.ParseArgs(args)
            
    def Execute(self):
        for package in self.packageManager.Packages():
            self.ExecutePackage(package)
            
    def ExecutePackage(self, package):
        package.findLatestVersion()
        print self.args['dir']
        package.download(self.args['dir'])
