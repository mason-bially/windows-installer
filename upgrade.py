import command

class Command(command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self,
            {'prog': "upgrade",
             'description': "Upgrades packages. NOT IMPLEMENTED!"})

    
