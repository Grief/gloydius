import hashlib, json, urllib2

from gloydius import *
from gloydius.fs import *
from gloydius.fs import path as p


def http_date(utc):
    weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][utc.weekday()]
    month   = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][utc.month - 1]
    return '{}, {:02} {} {:04} {:02}:{:02}:{:02} GMT'.format(weekday, utc.day, month, utc.year, utc.hour, utc.minute, utc.second)

def web_page_file(url, referer=None):
    page_file = p(GLOYDIUS_CACHE, hashlib.md5(url).hexdigest())
    last_time = utc_mtime(page_file)
    request   = urllib2.Request(url)
    if referer   is not None: request.add_header('Referer', referer)
    if last_time is not None: request.add_header('If-Modified-Since', http_date(last_time))
    try:
        response = urllib2.urlopen(request)
        print 'Downloading {} bytes'.format(int(response.info()['content-length']))
        write_file(page_file, response.read())
        print "Complete!"
    except urllib2.HTTPError as e: print "'{}' ERROR".format(url), e
    return page_file

def get_json(url): return json.loads(urllib2.urlopen(url).read())

def find_on_page(url, pattern):
    return pattern.search(read_file(web_page_file(url))).group(1)