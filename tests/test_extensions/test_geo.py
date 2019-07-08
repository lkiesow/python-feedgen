import unittest

from lxml import etree

from feedgen.feed import FeedGenerator


class TestExtensionGeo(unittest.TestCase):

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('geo')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_geoEntryItems(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.geo.point('42.36 -71.05')

        assert fe.geo.point() == '42.36 -71.05'

        # Check that we have the item in the resulting XML
        ns = {'georss': 'http://www.georss.org/georss'}
        root = etree.fromstring(self.fg.rss_str())
        point = root.xpath('/rss/channel/item/georss:point/text()',
                           namespaces=ns)
        assert point == ['42.36 -71.05']
