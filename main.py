import os
import command, install, upgrade, fetch, version

import command
import packagemanager

commandList = {
            "install":(install.Command,
                       "Installs packages."),
            "upgrade":(upgrade.Command,
                       "Upgrades packages."),
            "fetch":(fetch.Command,
                       "Downloads packages."),
            "version":(version.Command,
                       "Reports information about current packages.")}


class CommandLine():
    def __init__ (self):
        pass

    def Execute(self, argv):
        global commandList
        
        command = commandList[argv[0]][0](argv[1:])
        if command == None:
            raise Exception("Invalid command")
        else:
            command.Execute()
            return True

    def ValidCommand(self, argv):
        return argv[0] in commandList

    def Help(self):
        global commandList
        
        print "Below are the valid commands:"
        for key, command in commandList.iteritems():
            print '\t', key, '\n\t  ', command[1]


if __name__ == "__main__":
    commandLine = CommandLine()
    argv = os.sys.argv[1:]
    if len(os.sys.argv) == 1 or not commandLine.ValidCommand(argv):
        commandLine.Help()
    else:
        try:
            commandLine.Execute(argv)
        except Exception as e:
            print e
