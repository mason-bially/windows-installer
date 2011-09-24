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
        command.Execute()

if __name__ == "__main__":
    commandLine = CommandLine()
    commandLine.Execute(os.sys.argv[1:])
