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

from twisted.web import server, resource
from twisted.internet import reactor, ssl
from ConfigParser import SafeConfigParser

from urlclean import unshorten
from pcd import PersistentCryptoDict
from random_agent import RandomAgent

cfg = SafeConfigParser()
cfg.read('/etc/anonshort.cfg')
cfg.read('anonshort.cfg')

class Simple(resource.Resource):
    isLeaf = True
    cache = PersistentCryptoDict()
    def render_GET(self, request):
        if request.args and len(request.args.get('u')):
            try:
                kwargs={'proxyhost': cfg.get('proxy','host'),
                        'proxyport': cfg.get('proxy','port')}
            except:
                kwargs={}
            return unshorten(request.args.get('u')[0],
                             ua=RandomAgent(cfg.get('resolver','db')).get_agent,
                             cache=self.cache,
                             **kwargs)
        return "Error: try appending ?u=<URL>"

if __name__ == "__main__":
    site = server.Site(Simple())
    reactor.listenTCP(cfg.getint('anonshort','port'), site)
    if cfg.has_section('ssl'):
        # start ssl listener if configured
        reactor.listenSSL(cfg.getint('ssl','port'),
                          site,
                          ssl.DefaultOpenSSLContextFactory(cfg.get('ssl','key'),
                                                           cfg.get('ssl','cert')))
    reactor.run()
