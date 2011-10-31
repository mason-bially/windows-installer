import os, argparse, logging, traceback, sys
import packagemanager, ourlogging

class Base():
    """Base command class"""
    def __init__(self, argument_parser = {}):
        self.parser = argparse.ArgumentParser(**argument_parser)
        self.args = {}
        self.logger = None

        self.parser.add_argument('--debug', dest="debug",
                                action='store_true',
                                help="Enable debugging information")
        self.parser.add_argument('-q', dest="quiet", default=0,
                                action='store_const', const=1,
                                help="Quiet info messages.")
        self.parser.add_argument('-qq', dest="quiet", default=0,
                                action='store_const', const=2,
                                help="Quiet all extra messages.")
        self.parser.add_argument('--log-file', dest="log-file",
                                default='default.log',
                                help="The output log file.")
        
    def ParseArgs(self, args):
        self.args = vars(self.parser.parse_args(args))
        loggingConfig = {}
        
        if not ourlogging.configured:
            if self.args['debug']:
                loggingConfig['debugInfo'] = True
                loggingConfig['consoleLevel'] = logging.DEBUG  
            elif self.args['quiet'] == 1:
                loggingConfig['consoleLevel'] = logging.WARNING
            elif self.args['quiet'] == 2:
                loggingConfig['consoleLevel'] = logging.ERROR

            loggingConfig['fileName'] = self.args['log-file']

            ourlogging.config(**loggingConfig)

        self.logger = ourlogging.commandLogger(self.parser.prog)
        
    def Execute(self):
        pass

class BasePackageCommand(Base):
    """Adds functionality to make package based commands easier to write"""
    def __init__(self, argument_parser = {}):
        Base.__init__(self, argument_parser)

        #If this slot is set and true then the packages list is optional
        if 'runAllPackagesDefault' in self.__dict__ and self.runAllPackagesDefault:
            my_nargs = '*'
        else:
            my_nargs = '+'
            self.runAllPackagesDefault = False
            
        self.parser.add_argument('packages', nargs=my_nargs,
                                 default=None,
                                 help="list of packages to perform this action on")
        
        self.packageManager = packagemanager.PackageManager()
        

    def ParseArgs(self, args):
        Base.ParseArgs(self, args)
        if self.args['packages'] != []:
            self.logger.debug("Loding packages: " + str(self.args['packages']))
            self.packageManager.LoadPackages(map(lambda x: '_'+x, self.args['packages']))

        else:
            if self.runAllPackagesDefault:
                self.logger.debug("Loding all packages.")
                self.packageManager.LoadPackages(None)
            else:
                self.logger.debug("Loding no packages.")
                self.packageManager.LoadPackages([])


    def ExecutePackages(self):
        for package in self.packageManager.Packages():
            try:
                self.ExecutePackage(package)
            except Exception as e:
                self.logger.error("Package '" + package.name() + "' threw exception: \"" + str(e) + '"')
                self.logger.debug("Full stacktrace:\n+" + "+".join(traceback.format_tb(sys.exc_info()[2])))
            
        
    def Execute(self):
        self.ExecutePackages()

#################################
# Shared argument specifications

def AttachDownloadArgument(self):
    """Attaches download directory arguments to the command's parser"""
    self.parser.add_argument('-d', '--download-directory', dest="dir",
                            default="downloads",
                            help="Directory to download files to.")
