import command
import packagemanager

class Command(command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self, args)

    def Execute(self):
        for package in self.packageManager.AllPackages():
            package.download()
