from logging import *

configured = False
rootLogger = None

def config(consoleLevel=INFO, fileName='default.log', debugInfo=False):
    global configured
    global rootLogger
    
    rootLogger = getLogger()
    rootLogger.setLevel(DEBUG)

    #File Handler
    fh = FileHandler(fileName)
    fh.setLevel(DEBUG)

    #Console Handler
    ch = StreamHandler()
    ch.setLevel(consoleLevel)

    #The formmatter
    if debugInfo:
        f = Formatter('%(module)-12s:%(lineno)-3s ++ %(packageorcommand)-14s %(levelname)-8s - %(message)s')
    else:
        f = Formatter('%(packageorcommand)-14s %(levelname)-8s - %(message)s')
    ch.setFormatter(f)
    fh.setFormatter(f)
    
    rootLogger.addHandler(fh)
    rootLogger.addHandler(ch)

    configured = True

def packageLogger(package):
    return LoggerAdapter(getLogger(package), {'packageorcommand': '|-'+package})

def commandLogger(command):
    return LoggerAdapter(getLogger(command), {'packageorcommand': command})
                                              
def otherLogger(name):
    return LoggerAdapter(getLogger(command), {'packageorcommand': ' * '+name})
