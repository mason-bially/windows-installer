NOTES ON CREATING A PACKAGE:
Each package must contain the following:
	1) Its own subfolder starting with an _ then packagename (must not start with a double underscore) (<foldername>
	2) A python file containing named <foldername>.py containing a class named <foldername> which should be a
	subclass of packagesbaseclass.package.Package
	3) a config file named <foldername>.cfg
	4) FOR THE LOVE OF GOD IF THE DOWNLOAD LINK CONTAINS A VERSION NUMBER THEN #VERSION# OR #DOTLESSVERSION#
	Must replace the number. Otherwise the package downloads the same version every single time.