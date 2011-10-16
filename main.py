import os
import command, install, upgrade, fetch, version

import command
import packagemanager

commandList = {}

class HelpCommand(command.BasePackageCommand):
    def __init__(self, args):
        command.BasePackageCommand.__init__(self, args)

    def Execute(self):
        global commandList
        if len(self.args['']) > 0:
            command = self.args[''][0]
            if command in commandList:
                print "Below are the options for the '" + command + "' command:"
                commandList[command][0]("").PrintHelp()

commandList = {
            "install":(install.Command,
                       "Installs packages."),
            "upgrade":(upgrade.Command,
                       "Upgrades packages."),
            "fetch":(fetch.Command,
                       "Downloads packages."),
            "version":(version.Command,
                       "Reports information about current packages."),
            "help":(HelpCommand,
                       "Prints out help about the command.")}


class CommandLine():
    def __init__ (self):
        pass

    def Execute(self, argv):
        global commandList
        
        command = commandList[argv[0]][0](argv[1:])
        if command == None:
            return False
        else:
            command.Execute()
            return True

    def Help(self):
        global commandList
        
        print "Below are the valid commands:"
        for key, command in self.commandList.iteritems():
            print '\t', key, '\n\t  ', command[1]


if __name__ == "__main__":
    commandLine = CommandLine()
    if len(os.sys.argv) == 1 or not commandLine.Execute(os.sys.argv[1:]):
        commandLine.Help()
