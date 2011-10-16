import command
import packagemanager

class Command(command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self, args)
        if self.args['p'] == []:
            self.packageManager.LoadPackages(None)
        else:
            self.packageManager.LoadPackages(self.args['p'])


    def Execute(self):
        for package in self.packageManager.Packages():
            print package
