# -*- coding: utf-8 -*-
'''
    feedgen.ext.geo_entry
    ~~~~~~~~~~~~~~~~~~~

    Extends the FeedGenerator to produce Simple GeoRSS feeds.

    :copyright: 2017, Bob Breznak <bob.breznak@gmail.com>

    :license: FreeBSD and LGPL, see license.* for more details.
'''
import numbers

from lxml import etree
from feedgen.ext.base import BaseEntryExtension


class GeoEntryExtension(BaseEntryExtension):
    '''FeedEntry extension for Simple GeoRSS.
    '''

    def __init__(self):
        '''Simple GeoRSS tag'''
        # geometries
        self.__point = None
        self.__line = None
        self.__polygon = None
        self.__box = None

        # additional properties
        self.__featuretypetag = None
        self.__relationshiptag = None
        self.__featurename = None

        # elevation
        self.__elev = None
        self.__floor = None

        # radius
        self.__radius = None

    def extend_file(self, entry):
        '''Add additional fields to an RSS item.

        :param feed: The RSS item XML element to use.
        '''

        GEO_NS = 'http://www.georss.org/georss'

        if self.__point:
            point = etree.SubElement(entry, '{%s}point' % GEO_NS)
            point.text = self.__point

        if self.__line:
            line = etree.SubElement(entry, '{%s}line' % GEO_NS)
            line.text = self.__line

        if self.__polygon:
            polygon = etree.SubElement(entry, '{%s}polygon' % GEO_NS)
            polygon.text = self.__polygon

        if self.__box:
            box = etree.SubElement(entry, '{%s}box' % GEO_NS)
            box.text = self.__box

        if self.__featuretypetag:
            featuretypetag = etree.SubElement(entry, '{%s}featuretypetag' % GEO_NS)
            featuretypetag.text = self.__featuretypetag

        if self.__relationshiptag:
            relationshiptag = etree.SubElement(entry, '{%s}relationshiptag' % GEO_NS)
            relationshiptag.text = self.__relationshiptag

        if self.__featurename:
            featurename = etree.SubElement(entry, '{%s}featurename' % GEO_NS)
            featurename.text = self.__featurename

        if self.__elev:
            elevation = etree.SubElement(entry, '{%s}elev' % GEO_NS)
            elevation.text = self.__elev

        if self.__floor:
            floor = etree.SubElement(entry, '{%s}floor' % GEO_NS)
            floor.text = self.__floor

        if self.__radius:
            radius = etree.SubElement(entry, '{%s}radius' % GEO_NS)
            radius.text = self.__radius

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

    def line(self, line=None):
        '''Get or set the georss:line of the entry

        :param point: The GeoRSS formatted line (i.e. "45.256 -110.45 46.46 -109.48 43.84 -109.86")
        :return: The current georss:line of the entry
        '''
        if line is not None:
            self.__line = line

        return self.__line

    def polygon(self, polygon=None):
        '''Get or set the georss:polygon of the entry

        :param polygon: The GeoRSS formatted polygon (i.e. "45.256 -110.45 46.46 -109.48 43.84 -109.86 45.256 -110.45")
        :return: The current georss:polygon of the entry
        '''
        if polygon is not None:
            self.__polygon = polygon

        return self.__polygon

    def box(self, box=None):
        '''
        Get or set the georss:box of the entry

        :param box: The GeoRSS formatted box (i.e. "42.943 -71.032 43.039 -69.856")
        :return: The current georss:box of the entry
        '''
        if box is not None:
            self.__box = box

        return self.__box

    def featuretypetag(self, featuretypetag):
        '''
        Get or set the georss:featuretypetag of the entry

        :param featuretypetag: The GeoRSS feaaturertyptag (e.g. "city")
        :return: The current georss:featurertypetag
        '''
        if featuretypetag is not None:
            self.__featuretypetag = featuretypetag

        return self.__featuretypetag

    def relationshiptag(self, relationshiptag):
        '''
        Get or set the georss:relationshiptag of the entry

        :param relationshiptag: The GeoRSS relationshiptag (e.g. "is-centred-at")
        :return: the current georss:relationshiptag
        '''
        if relationshiptag is not None:
            self.__relationshiptag = relationshiptag

        return self.__relationshiptag

    def featurename(self, featurename):
        '''
        Get or set the georss:featurename of the entry

        :param featuretypetag: The GeoRSS featurename (e.g. "city")
        :return: the current georss:featurename
        '''
        if featurename is not None:
            self.__featurename = featurename

        return self.__featurename

    def elev(self, elev):
        '''
        Get or set the georss:elev of the entry

        :param elev: The GeoRSS elevation (e.g. 100.3)
        :type elev: numbers.Number
        :return: the current georss:elev
        '''
        if elev is not None:
            if not isinstance(elev, numbers.Number):
                raise ValueError("elev tag must be numeric: {}".format(elev))

            self.__elev = elev

        return self.__elev

    def floor(self, floor):
        '''
        Get or set the georss:floor of the entry

        :param floor: The GeoRSS floor (e.g. 4)
        :type floor: int
        :return: the current georss:floor
        '''
        if floor is not None:
            if not isinstance(floor, int):
                raise ValueError("floor tag must be int: {}".format(floor))

            self.__floor = floor

        return self.__floor

    def radius(self, radius):
        '''
        Get or set the georss:radius of the entry

        :param radius: The GeoRSS radius (e.g. 100.3)
        :type radius: numbers.Number
        :return: the current georss:radius
        '''
        if radius is not None:
            if not isinstance(radius, numbers.Number):
                raise ValueError("radius tag must be numeric: {}".format(radius))

            self.__radius = radius

        return self.__radius
