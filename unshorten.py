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
UADB='agents.db'
DEFAULTUA='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

import re, urllib2, cookielib, time, sys
from urlparse import urlparse, urlunparse
from itertools import ifilterfalse
import urllib, httplib
from lxml.html.soupparser import parse
from cache import get, set
from random_agent import RandomAgent

utmRe=re.compile('utm_(source|medium|campaign|content|term)=')
def urlSanitize(url):
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
    if UADB and us.netloc not in ['t.co']:
        ua=RandomAgent(UADB).get_agent()
    else:
        ua=DEFAULTUA
    headers={'User-Agent': ua,
             'Accept': '*/*',}
    conn.request("GET", url, None, headers)
    res = conn.getresponse()
    if res.status in [301, 304]:
        url = res.getheader('Location')
    # removes annoying UTM params to urls.
    pcs=urlparse(urllib.unquote_plus(url))
    tmp=list(pcs)
    tmp[4]='&'.join(ifilterfalse(utmRe.match, pcs.query.split('&')))
    root=None
    if res and res.getheader('Content-type')=='text/html':
        root=parse(res)
    return (urlunparse(tmp), root)

def unmeta(url,root):
    for x in root.xpath('//meta[@http-equiv="refresh"]'):
        newurl=x.get('content').split('; ')
        if len(newurl)>1:
            parts=urlparse(urllib.unquote_plus(newurl[1]))
            if parts['scheme'] and parts['netloc'] and parts['path']:
                url=newurl
    return url

def unshorten(url):
    prev=None
    origurl=url
    seen=[]
    while url!=prev:
        if url in seen: return ""
        seen.append(url)
        cached=get(url)
        if cached: return cached
        prev=url
        url,root=urlSanitize(url)
        if root:
            url=unmeta(url,root)
    set(origurl,url)
    return url

if __name__ == "__main__":
    url="http://bit.ly/xJ5pK2"
    if len(sys.argv)>1:
        url=sys.argv[1]
    print unshorten(url)
