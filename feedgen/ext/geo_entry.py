# -*- coding: utf-8 -*-
'''
    feedgen.ext.geo_entry
    ~~~~~~~~~~~~~~~~~~~

    Extends the FeedGenerator to produce Simple GeoRSS feeds.

    :copyright: 2017, Bob Breznak <bob.breznak@gmail.com>

    :license: FreeBSD and LGPL, see license.* for more details.
'''

from lxml import etree
from feedgen.ext.base import BaseEntryExtension


class GeoEntryExtension(BaseEntryExtension):
    '''FeedEntry extension for Simple GeoRSS.
    '''

    def __init__(self):
        # Simple GeoRSS tag
        self.__point = None

    def extend_file(self, entry):
        '''Add additional fields to an RSS item.

        :param feed: The RSS item XML element to use.
        '''

        GEO_NS = 'http://www.georss.org/georss'

        if self.__point:
            point = etree.SubElement(entry, '{%s}point' % GEO_NS)
            point.text = self.__point

        return entry

    def extend_rss(self, entry):
        return self.extend_file(entry)

    def extend_atom(self, entry):
        return self.extend_file(entry)

    def point(self, point=None):
        '''Get or set the georss:point of the entry.

        :param point: The GeoRSS formatted point (i.e. "42.36 -71.05")
        :returns: The current georss:point of the entry.
        '''

        if point is not None:
            self.__point = point

        return self.__point
