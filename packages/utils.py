import urllib2
import re

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
        ret = re.findall(reg, getPage(url))
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
    