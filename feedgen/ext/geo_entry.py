# -*- coding: utf-8 -*-
'''
    feedgen.ext.geo_entry
    ~~~~~~~~~~~~~~~~~~~

    Extends the FeedGenerator to produce Simple GeoRSS feeds.

    :copyright: 2017, Bob Breznak <bob.breznak@gmail.com>

    :license: FreeBSD and LGPL, see license.* for more details.
'''
import numbers
import warnings

from feedgen.ext.base import BaseEntryExtension
from feedgen.util import xml_elem


class GeoRSSPolygonInteriorWarning(Warning):
    """
    Simple placeholder for warning about ignored polygon interiors.

    Stores the original geom on a ``geom`` attribute (if required warnings are
    raised as errors).
    """

    def __init__(self, geom, *args, **kwargs):
        self.geom = geom
        super(GeoRSSPolygonInteriorWarning, self).__init__(*args, **kwargs)

    def __str__(self):
        return '{:d} interiors of polygon ignored'.format(
            len(self.geom.__geo_interface__['coordinates']) - 1
        )  # ignore exterior in count


class GeoRSSGeometryError(ValueError):
    """
    Subclass of ValueError for a GeoRSS geometry error

    Only some geometries are supported in Simple GeoRSS, so if not raise an
    error. Offending geometry is stored on the ``geom`` attribute.
    """

    def __init__(self, geom, *args, **kwargs):
        self.geom = geom
        super(GeoRSSGeometryError, self).__init__(*args, **kwargs)

    def __str__(self):
        msg = "Geometry of type '{}' not in Point, Linestring or Polygon"
        return msg.format(
            self.geom.__geo_interface__['type']
        )


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
            point = xml_elem('{%s}point' % GEO_NS, entry)
            point.text = self.__point

        if self.__line:
            line = xml_elem('{%s}line' % GEO_NS, entry)
            line.text = self.__line

        if self.__polygon:
            polygon = xml_elem('{%s}polygon' % GEO_NS, entry)
            polygon.text = self.__polygon

        if self.__box:
            box = xml_elem('{%s}box' % GEO_NS, entry)
            box.text = self.__box

        if self.__featuretypetag:
            featuretypetag = xml_elem('{%s}featuretypetag' % GEO_NS, entry)
            featuretypetag.text = self.__featuretypetag

        if self.__relationshiptag:
            relationshiptag = xml_elem('{%s}relationshiptag' % GEO_NS, entry)
            relationshiptag.text = self.__relationshiptag

        if self.__featurename:
            featurename = xml_elem('{%s}featurename' % GEO_NS, entry)
            featurename.text = self.__featurename

        if self.__elev:
            elevation = xml_elem('{%s}elev' % GEO_NS, entry)
            elevation.text = str(self.__elev)

        if self.__floor:
            floor = xml_elem('{%s}floor' % GEO_NS, entry)
            floor.text = str(self.__floor)

        if self.__radius:
            radius = xml_elem('{%s}radius' % GEO_NS, entry)
            radius.text = str(self.__radius)

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

        :param point: The GeoRSS formatted line (i.e. "45.256 -110.45 46.46
                      -109.48 43.84 -109.86")
        :return: The current georss:line of the entry
        '''
        if line is not None:
            self.__line = line

        return self.__line

    def polygon(self, polygon=None):
        '''Get or set the georss:polygon of the entry

        :param polygon: The GeoRSS formatted polygon (i.e. "45.256 -110.45
                        46.46 -109.48 43.84 -109.86 45.256 -110.45")
        :return: The current georss:polygon of the entry
        '''
        if polygon is not None:
            self.__polygon = polygon

        return self.__polygon

    def box(self, box=None):
        '''
        Get or set the georss:box of the entry

        :param box: The GeoRSS formatted box (i.e. "42.943 -71.032 43.039
                    -69.856")
        :return: The current georss:box of the entry
        '''
        if box is not None:
            self.__box = box

        return self.__box

    def featuretypetag(self, featuretypetag=None):
        '''
        Get or set the georss:featuretypetag of the entry

        :param featuretypetag: The GeoRSS feaaturertyptag (e.g. "city")
        :return: The current georss:featurertypetag
        '''
        if featuretypetag is not None:
            self.__featuretypetag = featuretypetag

        return self.__featuretypetag

    def relationshiptag(self, relationshiptag=None):
        '''
        Get or set the georss:relationshiptag of the entry

        :param relationshiptag: The GeoRSS relationshiptag (e.g.
                                "is-centred-at")
        :return: the current georss:relationshiptag
        '''
        if relationshiptag is not None:
            self.__relationshiptag = relationshiptag

        return self.__relationshiptag

    def featurename(self, featurename=None):
        '''
        Get or set the georss:featurename of the entry

        :param featuretypetag: The GeoRSS featurename (e.g. "Footscray")
        :return: the current georss:featurename
        '''
        if featurename is not None:
            self.__featurename = featurename

        return self.__featurename

    def elev(self, elev=None):
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

    def floor(self, floor=None):
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

    def radius(self, radius=None):
        '''
        Get or set the georss:radius of the entry

        :param radius: The GeoRSS radius (e.g. 100.3)
        :type radius: numbers.Number
        :return: the current georss:radius
        '''
        if radius is not None:
            if not isinstance(radius, numbers.Number):
                raise ValueError(
                    "radius tag must be numeric: {}".format(radius)
                )

            self.__radius = radius

        return self.__radius

    def geom_from_geo_interface(self, geom):
        '''
        Generate a georss geometry from some Python object with a
        ``__geo_interface__`` property (see the `geo_interface specification by
        Sean Gillies`_geointerface )

        Note only a subset of GeoJSON (see `geojson.org`_geojson ) can be
        easily converted to GeoRSS:

        - Point
        - LineString
        - Polygon (if there are holes / donuts in the polygons a warning will
          be generaated

        Other GeoJson types will raise a ``ValueError``.

        .. note:: The geometry is assumed to be x, y as longitude, latitude in
           the WGS84 projection.

        .. _geointerface: https://gist.github.com/sgillies/2217756
        .. _geojson: https://geojson.org/

        :param geom: Geometry object with a __geo_interface__ property
        :return: the formatted GeoRSS geometry
        '''
        geojson = geom.__geo_interface__

        if geojson['type'] not in ('Point', 'LineString', 'Polygon'):
            raise GeoRSSGeometryError(geom)

        if geojson['type'] == 'Point':

            coords = '{:f} {:f}'.format(
                geojson['coordinates'][1],  # latitude is y
                geojson['coordinates'][0]
            )
            return self.point(coords)

        elif geojson['type'] == 'LineString':

            coords = ' '.join(
                '{:f} {:f}'.format(vertex[1], vertex[0])
                for vertex in
                geojson['coordinates']
            )
            return self.line(coords)

        elif geojson['type'] == 'Polygon':

            if len(geojson['coordinates']) > 1:
                warnings.warn(GeoRSSPolygonInteriorWarning(geom))

            coords = ' '.join(
                '{:f} {:f}'.format(vertex[1], vertex[0])
                for vertex in
                geojson['coordinates'][0]
            )
            return self.polygon(coords)
