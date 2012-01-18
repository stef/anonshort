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


import re, urllib2, cookielib, time
from urlparse import urlparse, urlunparse
from itertools import ifilterfalse
import urllib, httplib
from lxml.html.soupparser import parse

opener=None
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
                              urllib2.ProxyHandler({'http': 'http://localhost:8123/'}))
opener.addheaders = [('User-agent', 'parltrack/0.6')]
def fetch(url, retries=5, ignore=[]):
    if not opener:
        init_opener()
    # url to etree
    try:
        f=opener.open(url)
    except (urllib2.HTTPError, urllib2.URLError), e:
        if hasattr(e, 'code') and e.code>=400 and e.code not in [504, 502]+ignore:
            logger.warn("[!] %d %s" % (e.code, url))
            raise
        if retries>0:
            time.sleep(4*(6-retries))
            f=fetch(url,retries-1, ignore=ignore)
        else:
            raise
    return parse(f)

utmRe=re.compile('utm_(source|medium|campaign|content)=')
def urlSanitize(url, ua=None):
    # handle any redirected urls from the feed, like
    # ('http://feedproxy.google.com/~r/Torrentfreak/~3/8UY1UySQe1k/')
    us=httplib.urlsplit(url)
    if us.scheme=='http':
        conn = httplib.HTTPConnection(us.netloc)
        req = urllib.quote(url[7+len(us.netloc):])
    elif us.scheme=='https':
        conn = httplib.HTTPSConnection(us.netloc)
        req = urllib.quote(url[8+len(us.netloc):])
    #conn.set_debuglevel(9)
    headers={'User-Agent': ua or 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    conn.request("HEAD", req,None,headers)
    res = conn.getresponse()
    if res.status in [301, 304]:
        url = res.getheader('Location')
    # removes annoying UTM params to urls.
    pcs=urlparse(urllib.unquote_plus(url))
    tmp=list(pcs)
    tmp[4]='&'.join(ifilterfalse(utmRe.match, pcs.query.split('&')))
    return urlunparse(tmp)

def unmeta(url):
    for x in fetch(url).xpath('//meta[@http-equiv="refresh"]'):
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
        url=urlSanitize(url,ua=ua)
        url=unmeta(url)
    return url

url="http://bit.ly/xJ5pK2"
print unshorten(url)
