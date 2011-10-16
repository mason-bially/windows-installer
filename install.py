import command

class Command(command.BasePackageCommand):
    def __init__(self, args):
        self.argDescription = {
            'q': {'maxSize': 0, 'description':
                   "Run the command quietly."},
            'v': {'maxSize': 0, 'description':
                   "Do not attempt to run installers quietly."},
            '-no-fetch': {'maxSize': 0, 'description':
                   "Does not fetch the packages, will report an error for each package that doesn't have an installer already fetched."},
            }
        
        command.BasePackageCommand.__init__(self, args)
        
    def Execute(self):
        for package in self.packageManager.AllPackages():
            self.ExecutePackage(package)
            
    def ExecutePackage(self, package):
        if not '-no-fetch' in self.argDescription:
            package.download()

        package.install(not 'v' in self.argDescription)
            
