# -*- coding: utf-8 -*-
'''
    feedgen.ext.geo
    ~~~~~~~~~~~~~~~~~~~

    Extends the FeedGenerator to produce Simple GeoRSS feeds.

    :copyright: 2017, Bob Breznak <bob.breznak@gmail.com>

    :license: FreeBSD and LGPL, see license.* for more details.
'''

from feedgen.ext.base import BaseExtension


class GeoExtension(BaseExtension):
    '''FeedGenerator extension for Simple GeoRSS.
    '''

    def extend_ns(self):
        return {'georss': 'http://www.georss.org/georss'}
