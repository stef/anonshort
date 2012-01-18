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


from unshorten import unshorten
from twisted.web import server, resource
from twisted.internet import reactor

class Simple(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        if request.args and len(request.args.get('u')):
            return unshorten(request.args.get('u')[0])

site = server.Site(Simple())
reactor.listenTCP(8080, site)
reactor.run()
