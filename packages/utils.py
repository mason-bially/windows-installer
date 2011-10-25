import urllib2
import re
from BeautifulSoup import BeautifulSoup

def getPage(url):
    """Returns the contents of a url as a string.

    This currently doesn't do anything to handle exceptions.

    @param url The url to grab a page from.
    @return A string containing the page contents of url.
    """
    try:
        f = urllib2.urlopen(url)
        page = f.read()
        f.close()
    except urllib2.URLError:
        print 'Couldn not connect to and read from %s' % url
    except:
        print 'unknown error running  getPage(%s)' % url
        raise
    else:
        return page
    
def scrapePage(reg, url):
    """Scrapes the page from url for the reg at position pos.

    Returns all matches of reg on page URL. If no matches are found
    and error is returned.

    @param reg The regular expression to match.
    @param url The page to scrape.
    @return The pos'th reg match on the page at url.
    """
    try:
        ret = re.findall(reg, getPage(url), re.IGNORECASE)
    except TypeError as strerror:
        if strerror == 'first argument must be a string or compiled pattern':
            print 'you are missing or have an invalid regex in %s' % reg
        elif strerror == 'expected string or buffer':
            print 'your have no page being returned by getPage()'
        print 'when calling scrapePage(%s, %s)' %(reg, url)
    except:
        print 'unknown error running  scrapePage(%s, %s)' % (reg, url)
        raise
    else:
        if ret == []:
            print "No Matches for '%s' found on '%s'" % (reg, url)
            raise IndexError("No Matches found on page")
        return ret

def parsePage(reg, url):
    # TO DO: Figure out how to pick the correct link.
    #        Just chooses first one now.
    try:
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        page.close()
    except urllib2.URLError:
        print 'Couldn not connect to and read from %s' % url
    except:
        print 'unknown error running  parsePage(%s)' % url
        raise
    else:
        #use linkRegex to find useful links, possible downloads
        links = soup.fetch(lambda(x): x.name=='a' and re.search(reg, repr(x.string), re.IGNORECASE) != None)
        return links[0]['href']
    
def downloadFile(URL, directory, fileName):
    """Downloads a given URL to directory"""
    try:
        f = urllib2.urlopen(URL)
        fileContents = f.read()
        extension = "." + f.geturl().split(".")[-1]
        f.close()
        downloadpath = directory + '/' + fileName + extension
        if not directory.endswith("/"):
            directory = directory + "/"
        with open(downloadpath, "wb") as downloadedFile:
            downloadedFile.write(fileContents)
        return downloadpath
    except urllib2.HTTPError, e:
        print "ERROR DOWNLOADING: ", e.code, URL
        raise
    except urllib2.URLError, e:
        print "URL ERROR: " , e.reason, URL
        raise
    

def findInString(string, wordList):
    """Checks to see if any of the words in wordList are in string
    returns the first word from wordList that is found in string. Otherwise
    returns false"""
    for word in wordList:
        returnWord = word.upper()
        if string.upper().find(returnWord) != -1:
            return returnWord
    return False
    
def findGreaterCol(a, b):
    """Returns the greater of the two inputs
    Or either if they are equal"""
    try:
        if int(a) > int(b):
            return a
        else:
            return b
    except ValueError:
        if a.upper() == 'FINAL':
            return a
        if b.upper() == "FINAL":
            return b
        if a.upper() == 'BETA' and b.upper() == "ALPHA":
            return a
        else: #Otherwise a <= b so B is ok to return
            return b
            
def breakVersions(versions):
    """Takes in a list of strings (versions) and returns a list of lists
    where each list represents a version number broken up.
    For example "1.2.3 beta" will become ["1","2","3","BETA"]"""
    versionsSplit = []
    tempVersion = ""
    # Filter out blanks, they are not valid versions
    versions = filter(lambda a: a != '', versions)
    for version in versions:
        #Sanitize input by removing white space from start and end
        tempVersion = version.upper()
        tempVersion = tempVersion.split('.')
        tempVersion = [x.rstrip().lstrip() for x in tempVersion]
        #Check for beta or alpha
        lastPos = len(tempVersion) - 1
        hasBetaAlpha = findInString(tempVersion[lastPos], ["BETA", "ALPHA"])
        if hasBetaAlpha != False:
            lastPosStr = tempVersion[lastPos]
            tempVersion.pop(lastPos)
            #Catch case where alpha is the only version
            if tempVersion != []:
                tempVersion.append(lastPosStr.rstrip(hasBetaAlpha).rstrip())
            tempVersion.append(hasBetaAlpha)
        else:
            tempVersion.append("FINAL")
        versionsSplit.append(tempVersion)
    return versionsSplit

def brokenVersionToStr(versions):
    """Takes in a list of broken apart versions and converts them to strings and returns them
    as a list of strings"""
    returnList = []
    for version in versions:
        returnStr = ""
        for element in version:
            if element.isdigit():
                if returnStr != "":
                    returnStr = returnStr + "."
                returnStr = returnStr + element
            elif returnStr != "":
                if element != 'FINAL':
                    returnStr = returnStr + " " + element
            else:
                returnStr = element
        returnList.append(returnStr)
    return returnList
    
def findHighestVersion(versions):
    """Takes in a list of strings and returns the highest version formatted in a standard format:
    1.2.3 [ALPHA|BETA]"""
    # Do some fancy foot-work to make sure
    # There are no duplicates in versions
    # So helper function won't recurse forever
    tempList = breakVersions(versions)
    tempList = brokenVersionToStr(tempList)
    tempList = list(set(tempList))
    tempList = breakVersions(tempList)
    return findHighestVersionHelper(tempList,0)
    
def findHighestVersionHelper(versions, col):
    if len(versions) == 1:
        return brokenVersionToStr(versions)[0]
    else:
        maxVer = "0"
        for element in versions:
            maxVer = findGreaterCol(maxVer,element[col])
        returnList = []
        for element in versions:
            if element[col] == maxVer:
                returnList.append(element)
        return findHighestVersionHelper(returnList,col + 1)

def findInstalledVersions(pak):
    """Takes in a package and attempts to find the installed version(s) If the package is installed."""
    print "Sorry this appears to be a stub."
    
    
def findVersionsReg(pak):
    """Takes in a package and attempts to find version(s) in the registry"""
    # Attempt to find the version in the Uninstall Directory of the registry
    
    print "Sorry THis appears to be a stub"
