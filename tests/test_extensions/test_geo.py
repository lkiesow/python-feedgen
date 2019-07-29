from itertools import chain
import unittest
import warnings

from lxml import etree

from feedgen.feed import FeedGenerator
from feedgen.ext.geo_entry import GeoRSSPolygonInteriorWarning, GeoRSSGeometryError  # noqa: E501


class Geom(object):
    """
    Dummy geom to make testing easier

    When we use the geo-interface we need a class with a `__geo_interface__`
    property. Makes it easier for the other tests as well.

    Ultimately this could be used to generate dummy geometries for testing
    a wider variety of values (e.g. with the faker library, or the hypothesis
    library)
    """

    def __init__(self, geom_type, coords):
        self.geom_type = geom_type
        self.coords = coords

    def __str__(self):
        if self.geom_type == 'Point':

            coords = '{:f} {:f}'.format(
                self.coords[1],  # latitude is y
                self.coords[0]
            )
            return coords

        elif self.geom_type == 'LineString':

            coords = ' '.join(
                '{:f} {:f}'.format(vertex[1], vertex[0])
                for vertex in
                self.coords
            )
            return coords

        elif self.geom_type == 'Polygon':

            coords = ' '.join(
                '{:f} {:f}'.format(vertex[1], vertex[0])
                for vertex in
                self.coords[0]
            )
            return coords

        elif self.geom_type == 'Box':
            # box not really supported by GeoJSON, but it's a handy cheat here
            # for testing
            coords = ' '.join(
                '{:f} {:f}'.format(vertex[1], vertex[0])
                for vertex in
                self.coords
            )
            return coords[:2]

        else:
            return 'Not a supported geometry'

    @property
    def __geo_interface__(self):
        return {
            'type': self.geom_type,
            'coordinates': self.coords
        }


class TestExtensionGeo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.point = Geom('Point', [-71.05, 42.36])
        cls.line = Geom('LineString', [[-71.05, 42.36], [-71.15, 42.46]])
        cls.polygon = Geom(
            'Polygon',
            [[[-71.05, 42.36], [-71.15, 42.46], [-71.15, 42.36]]]
        )
        cls.box = Geom('Box', [[-71.05, 42.36], [-71.15, 42.46]])
        cls.polygon_with_interior = Geom(
            'Polygon',
            [
                [  # exterior
                    [0, 0],
                    [0, 1],
                    [1, 1],
                    [1, 0],
                    [0, 0]
                ],
                [  # interior
                    [0.25, 0.25],
                    [0.25, 0.75],
                    [0.75, 0.75],
                    [0.75, 0.25],
                    [0.25, 0.25]
                ]
            ]
        )

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('geo')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_point(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.point(str(self.point))

        self.assertEqual(fe.geo.point(), str(self.point))

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        point = root.xpath('/rss/channel/item/georss:point/text()',
                           namespaces=ns)
        self.assertEqual(point, [str(self.point)])

    def test_line(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.line(str(self.line))

        self.assertEqual(fe.geo.line(), str(self.line))

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        line = root.xpath(
            '/rss/channel/item/georss:line/text()',
            namespaces=ns
        )
        self.assertEqual(line, [str(self.line)])

    def test_polygon(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.polygon(str(self.polygon))

        self.assertEqual(fe.geo.polygon(), str(self.polygon))

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        poly = root.xpath(
            '/rss/channel/item/georss:polygon/text()',
            namespaces=ns
        )
        self.assertEqual(poly, [str(self.polygon)])

    def test_box(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.box(str(self.box))

        self.assertEqual(fe.geo.box(), str(self.box))

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        box = root.xpath(
            '/rss/channel/item/georss:box/text()',
            namespaces=ns
        )
        self.assertEqual(box, [str(self.box)])

    def test_featuretypetag(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.featuretypetag('city')

        self.assertEqual(fe.geo.featuretypetag(), 'city')

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        featuretypetag = root.xpath(
            '/rss/channel/item/georss:featuretypetag/text()',
            namespaces=ns
        )
        self.assertEqual(featuretypetag, ['city'])

    def test_relationshiptag(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.relationshiptag('is-centred-at')

        self.assertEqual(fe.geo.relationshiptag(), 'is-centred-at')

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        relationshiptag = root.xpath(
            '/rss/channel/item/georss:relationshiptag/text()',
            namespaces=ns
        )
        self.assertEqual(relationshiptag, ['is-centred-at'])

    def test_featurename(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.featurename('Footscray')

        self.assertEqual(fe.geo.featurename(), 'Footscray')

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        featurename = root.xpath(
            '/rss/channel/item/georss:featurename/text()',
            namespaces=ns
        )
        self.assertEqual(featurename, ['Footscray'])

    def test_elev(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.elev(100.3)

        self.assertEqual(fe.geo.elev(), 100.3)

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        elev = root.xpath(
            '/rss/channel/item/georss:elev/text()',
            namespaces=ns
        )
        self.assertEqual(elev, ['100.3'])

    def test_elev_fails_nonnumeric(self):
        fe = self.fg.add_item()
        fe.title('y')

        with self.assertRaises(ValueError):
            fe.geo.elev('100.3')

    def test_floor(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.floor(4)

        self.assertEqual(fe.geo.floor(), 4)

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        floor = root.xpath(
            '/rss/channel/item/georss:floor/text()',
            namespaces=ns
        )
        self.assertEqual(floor, ['4'])

    def test_floor_fails_nonint(self):
        fe = self.fg.add_item()
        fe.title('y')

        with self.assertRaises(ValueError):
            fe.geo.floor(100.3)

        with self.assertRaises(ValueError):
            fe.geo.floor('4')

    def test_radius(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.radius(100.3)

        self.assertEqual(fe.geo.radius(), 100.3)

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        radius = root.xpath(
            '/rss/channel/item/georss:radius/text()',
            namespaces=ns
        )
        self.assertEqual(radius, ['100.3'])

    def test_radius_fails_nonnumeric(self):
        fe = self.fg.add_item()
        fe.title('y')

        with self.assertRaises(ValueError):
            fe.geo.radius('100.3')

    def test_geom_from_geointerface_point(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.geom_from_geo_interface(self.point)

        self.assertEqual(fe.geo.point(), str(self.point))

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        point = root.xpath('/rss/channel/item/georss:point/text()',
                           namespaces=ns)
        self.assertEqual(point, [str(self.point)])

        coords = [float(c) for c in point[0].split()]

        try:
            self.assertCountEqual(
                coords,
                self.point.coords
            )
        except AttributeError:  # was assertItemsEqual in Python 2.7
            self.assertItemsEqual(
                coords,
                self.point.coords
            )

    def test_geom_from_geointerface_line(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.geom_from_geo_interface(self.line)

        self.assertEqual(fe.geo.line(), str(self.line))

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        line = root.xpath('/rss/channel/item/georss:line/text()',
                          namespaces=ns)
        self.assertEqual(line, [str(self.line)])

        coords = [float(c) for c in line[0].split()]

        try:
            self.assertCountEqual(
                coords,
                list(chain.from_iterable(self.line.coords))
            )
        except AttributeError:  # was assertItemsEqual in Python 2.7
            self.assertItemsEqual(
                coords,
                list(chain.from_iterable(self.line.coords))
            )

    def test_geom_from_geointerface_poly(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.geom_from_geo_interface(self.polygon)

        self.assertEqual(fe.geo.polygon(), str(self.polygon))

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        poly = root.xpath('/rss/channel/item/georss:polygon/text()',
                          namespaces=ns)
        self.assertEqual(poly, [str(self.polygon)])

        coords = [float(c) for c in poly[0].split()]

        try:
            self.assertCountEqual(
                coords,
                list(chain.from_iterable(self.polygon.coords[0]))
            )
        except AttributeError:  # was assertItemsEqual in Python 2.7
            self.assertItemsEqual(
                coords,
                list(chain.from_iterable(self.polygon.coords[0]))
            )

    def test_geom_from_geointerface_fail_other_geom(self):
        fe = self.fg.add_item()
        fe.title('y')

        with self.assertRaises(GeoRSSGeometryError):
            fe.geo.geom_from_geo_interface(self.box)

    def test_geom_from_geointerface_fail_requires_geo_interface(self):
        fe = self.fg.add_item()
        fe.title('y')

        with self.assertRaises(AttributeError):
            fe.geo.geom_from_geo_interface(str(self.box))

    def test_geom_from_geointerface_warn_poly_interior(self):
        """
        Test complex polygons warn as expected. Taken from

        https://stackoverflow.com/a/3892301/379566 and
        https://docs.python.org/2.7/library/warnings.html#testing-warnings
        """
        fe = self.fg.add_item()
        fe.title('y')

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            fe.geo.geom_from_geo_interface(self.polygon_with_interior)
            # Verify some things
            assert len(w) == 1
            assert issubclass(w[-1].category, GeoRSSPolygonInteriorWarning)

        self.assertEqual(fe.geo.polygon(), str(self.polygon_with_interior))

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        poly = root.xpath('/rss/channel/item/georss:polygon/text()',
                          namespaces=ns)
        self.assertEqual(poly, [str(self.polygon_with_interior)])

        coords = [float(c) for c in poly[0].split()]

        try:
            self.assertCountEqual(
                coords,
                list(chain.from_iterable(self.polygon_with_interior.coords[0]))
            )
        except AttributeError:  # was assertItemsEqual in Python 2.7
            self.assertItemsEqual(
                coords,
                list(chain.from_iterable(self.polygon_with_interior.coords[0]))
            )
