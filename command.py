import os, argparse, logging, traceback, sys
import packagemanager, ourlogging

class Base():
    """Base command class"""
    def __init__(self, argument_parser = {}):
        self.parser = argparse.ArgumentParser(**argument_parser)
        self.args = {}
        self.logger = None

    def InitArgParse(self):
        """Intialize argparse stuff"""
        #Add common arguments
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
        """Setup and run argparse"""
        #Intializes argparse
        self.InitArgParse()
        
        #Parses and unpacks the args
        self.args = vars(self.parser.parse_args(args))

        #Process configuration args
        self.PostParseArgs()
        
    def PostParseArgs(self):
        """Performs configuration based on parsed args"""
        loggingConfig = {}

        #Set up logging
        if not ourlogging.configured:
            #choose the correct level of logging
            if self.args['debug']:
                loggingConfig['debugInfo'] = True
                loggingConfig['consoleLevel'] = logging.DEBUG  
            elif self.args['quiet'] == 1:
                loggingConfig['consoleLevel'] = logging.WARNING
            elif self.args['quiet'] == 2:
                loggingConfig['consoleLevel'] = logging.ERROR

            #set the log file
            loggingConfig['fileName'] = self.args['log-file']

            #call the logging config file with the arguments we've set up.
            ourlogging.config(**loggingConfig)

        #Setup our logger based off of the name of the command being run.
        self.logger = ourlogging.commandLogger(self.parser.prog)
        self.logger.debug("Logger created, starting logging now.")
        
    def Execute(self):
        """Execute the command"""
        #Blank for this abstract class
        pass



class BasePackageCommand(Base):
    """Adds functionality to make package based commands easier to write"""
    def __init__(self, argument_parser = {}):
        Base.__init__(self, argument_parser)
        self.invertDefault = False
        #Intialize the package manager, which this class wraps
        self.packageManager = packagemanager.PackageManager()

    def InitInvertAllPackages(self):
        """Helper function for intializing packages"""
        self.invertDefault = True
        
    def InitArgParse(self):
        Base.InitArgParse(self)
        self.parser.add_argument('packages', nargs='*',
                                 default=None,
                                 help="List of packages to perform this action on.")
        
        self.parser.add_argument('--all-except', dest='all-except',
                                 action='store_true',
                                 help="Executes all packages, EXCPET those specified.")

    def PostParseArgs(self):
        Base.PostParseArgs(self)

        #Determines the list of packages we are proccessing.
        if self.args['all-except']:
            self.logger.debug("Loding all packages except: " + str(self.args['packages']))
            self.packageManager.LoadInversePackages(self.args['packages'])
        elif self.args['packages'] != []:
            self.logger.debug("Loding packages: " + str(self.args['packages']))
            self.packageManager.LoadPackages(map(lambda x: '_'+x, self.args['packages']))
        else:
            if self.invertDefault:
                self.logger.debug("Loding all packages.")
                self.packageManager.LoadAllPackages()
            else:
                self.logger.debug("Loading no packages.")
                self.packageManager.LoadPackages([])


    def PreparePackage(self, package):
        """Prepare a package to be used"""
        package.findLatestVersion()

    def ExecutePackages(self):
        """Executes over all the packages, calling ExecutePackage on each package"""
        for package in self.packageManager.Packages():
            #This prepares the packages needed variables
            self.logger.debug("Preparing package '" + package.name() + "'.")
            self.PreparePackage(package)
        
        for package in self.SortPackages(self.packageManager.Packages()):
            try:
                #This calls the functionality related to each class
                self.logger.debug("Executing functionality for '" + package.name() + "'")
                self.ExecutePackage(package)
            except Exception as e:
                self.logger.error("Package '" + package.name() + "' threw exception: \"" + str(e) + '"')
                self.logger.debug("Full stacktrace:\n+" + "+".join(traceback.format_tb(sys.exc_info()[2])))
            
    def SortPackages(self, packages):
        """Function to replace to add sorting"""
        return packages
    
    def Execute(self):
        self.ExecutePackages()

#################################
# Shared argument specifications

def AttachDownloadArgument(self):
    """Attaches download directory arguments to the command's parser"""
    self.parser.add_argument('-d', '--download-directory', dest="dir",
                            default="downloads",
                            help="Directory to download files to.")

class AttachNoScrape(BasePackageCommand):
    """Attaches scrape prevention to the command"""
    def InitArgParse(self):
        BasePackageCommand.InitArgParse(self)
        self.parser.add_argument('--no-scrape', dest="no-scrape",
                                action='store_true',
                                help="Prevent all web scraping.")

    def PreparePackage(self, package):
        if self.args['no-scrape']:
            self.logger.debug("Preventing scrape for package '" + package.name() + "'.")
        else:
            BasePackageCommand.PreparePackage(self, package)
