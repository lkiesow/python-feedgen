import unittest

from lxml import etree

from feedgen.feed import FeedGenerator


class TestExtensionSyndication(unittest.TestCase):

    SYN_NS = {'sy': 'http://purl.org/rss/1.0/modules/syndication/'}

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('syndication')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_update_period(self):
        for period_type in ('hourly', 'daily', 'weekly', 'monthly', 'yearly'):
            self.fg.syndication.update_period(period_type)
            root = etree.fromstring(self.fg.rss_str())
            a = root.xpath('/rss/channel/sy:UpdatePeriod',
                           namespaces=self.SYN_NS)
            assert a[0].text == period_type

    def test_update_frequency(self):
        for frequency in (1, 100, 2000, 100000):
            self.fg.syndication.update_frequency(frequency)
            root = etree.fromstring(self.fg.rss_str())
            a = root.xpath('/rss/channel/sy:UpdateFrequency',
                           namespaces=self.SYN_NS)
            assert a[0].text == str(frequency)

    def test_update_base(self):
        base = '2000-01-01T12:00+00:00'
        self.fg.syndication.update_base(base)
        root = etree.fromstring(self.fg.rss_str())
        a = root.xpath('/rss/channel/sy:UpdateBase', namespaces=self.SYN_NS)
        assert a[0].text == base
