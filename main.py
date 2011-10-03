import os
import command, install, upgrade, fetch, version

class CommandLine():
    def __init__ (self):
        self.commandList = {
            "install":install.Command,
            "upgrade":upgrade.Command,
            "fetch":fetch.Command,
            "version":version.Command}

    def Execute(self, command):
        command = self.commandList[command[0]](command[1:])
        if command == None:
            return False
        else:
            command.Execute()
            return True

if __name__ == "__main__":
    commandLine = CommandLine()
    if len(os.sys.argv) == 1 or not commandLine.Execute(os.sys.argv[1:]):
        print """Please refer to the list of valid commands:
*list commands here*"""
