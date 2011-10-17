import command
import packagemanager

class Command(command.BasePackageCommand):
    def __init__(self, args):
        self.argDescription = {
            'd': {'maxSize': 1, 'description':
                   "Directory to download installers to."},
            }
        command.BasePackageCommand.__init__(self, args)
        self.packageManager.LoadPackages(self.args['p'])
            
    def Execute(self):
        for package in self.packageManager.Packages():
            self.ExecutePackage(package)
            
    def ExecutePackage(self, package):
        package.findLatestVersion()
        package.download(self.args['d'][0])
