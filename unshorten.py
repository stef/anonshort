#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of anonshort
#
#  anonshort is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  anonshort is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with anonshort  If not, see <http://www.gnu.org/licenses/>.
#
# (C) 2012- by Stefan Marsiske, <stefan.marsiske@gmail.com>

PROXY={'host': "localhost",
       'port': 8118 }

import re, urllib2, cookielib, time
from urlparse import urlparse, urlunparse
from itertools import ifilterfalse
import urllib, httplib
from lxml.html.soupparser import parse

utmRe=re.compile('utm_(source|medium|campaign|content)=')
def urlSanitize(url, ua=None):
    # handle any redirected urls from the feed, like
    # ('http://feedproxy.google.com/~r/Torrentfreak/~3/8UY1UySQe1k/')
    us=httplib.urlsplit(url)
    if not PROXY:
        if us.scheme=='http':
            conn = httplib.HTTPConnection(us.netloc)
            req = urllib.quote(url[7+len(us.netloc):])
        elif us.scheme=='https':
            conn = httplib.HTTPSConnection(us.netloc)
            req = urllib.quote(url[8+len(us.netloc):])
    else:
        conn = httplib.HTTPConnection(PROXY['host'],PROXY['port'])
        req = url
    #conn.set_debuglevel(9)
    headers={'User-Agent': ua or 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    conn.request("GET", url, None, headers)
    res = conn.getresponse()
    if res.status in [301, 304]:
        url = res.getheader('Location')
    # removes annoying UTM params to urls.
    pcs=urlparse(urllib.unquote_plus(url))
    tmp=list(pcs)
    tmp[4]='&'.join(ifilterfalse(utmRe.match, pcs.query.split('&')))
    return (urlunparse(tmp), parse(res))

def unmeta(url,root):
    for x in root.xpath('//meta[@http-equiv="refresh"]'):
        newurl=x.get('content').split('; ')
        if len(newurl)>1:
            parts=urlparse(urllib.unquote_plus(newurl[1]))
            if parts['scheme'] and parts['netloc'] and parts['path']:
                url=newurl
    return url

def unshorten(url, ua=None):
    prev=None
    while url!=prev:
        prev=url
        url,root=urlSanitize(url,ua=ua)
        url=unmeta(url,root)
    return url

if __name__ == "__main__":
    url="http://bit.ly/xJ5pK2"
    print unshorten(url)
