import argparse
import os
import ConfigParser

parser = argparse.ArgumentParser(description='Create a new package in the current directory with a skeleton config file')
parser.add_argument('package-name', help="Name of the package to create should contain _x32 or _x64 and the program name ex: Firefox_x32. Spaces in program names should be replaced with an underscore")
parser.add_argument('-n', '--programName', dest='programName', help="Sets programName in the config file")
parser.add_argument('-u', '--url', dest='url', help="Sets url in the config file")
parser.add_argument('-d', '--directory', dest='dir', help="Sets the directory to create the package in. defaults to the current working directory")
parser.add_argument('-a', '--author', dest='author', help="Sets the author of the package")

args = vars(parser.parse_args())

for item in args:
    if args[item] == None:
        args[item] = ""


package_name = "_" + args['package-name']
if args['dir'] != "":
    path=args['dir'] + "/_" + args['package-name']
else:
    path=args['package-name']

if os.path.exists(path):
    print 'Error Package already exists exiting'
    exit(1)
else:
    os.mkdir(path)
    pyfile = open(path + "/" + package_name + ".py", 'w')
    cfgfile = open(path + "/" + package_name + ".cfg", 'w')
    initfile = open(path + "/" + "__init__.py", 'w')
    pytemplate = open('package_template.py')
    cfgtemplate = open('config_template.cfg')
    for line in pytemplate:
        line = line.replace("#PACKAGENAME#", package_name)
        line = line.replace("#AUTHOR#", args['author'])
        pyfile.write(line)
    for line in cfgtemplate:
        cfgfile.write(line)
    pytemplate.close()
    cfgtemplate.close()
    pyfile.close()
    cfgfile.close()
    initfile.close()
    config = ConfigParser.RawConfigParser()
    config.read(path+ "/" + package_name + ".cfg")
    config.set('main', 'programName', args['programName'])
    config.set('main', 'url', args['url'])
    with open(path+ "/" + package_name + ".cfg", 'wb') as configFile:
        config.write(configFile)
    
    
    
