import unittest

from lxml import etree

from feedgen.feed import FeedGenerator


class TestExtensionTorrent(unittest.TestCase):

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('torrent')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_podcastEntryItems(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.torrent.filename('file.xy')
        fe.torrent.infohash('123')
        fe.torrent.contentlength('23')
        fe.torrent.seeds('1')
        fe.torrent.peers('2')
        fe.torrent.verified('1')
        self.assertEqual(fe.torrent.filename(), 'file.xy')
        self.assertEqual(fe.torrent.infohash(), '123')
        self.assertEqual(fe.torrent.contentlength(), '23')
        self.assertEqual(fe.torrent.seeds(), '1')
        self.assertEqual(fe.torrent.peers(), '2')
        self.assertEqual(fe.torrent.verified(), '1')

        # Check that we have the item in the resulting XML
        ns = {'torrent': 'http://xmlns.ezrss.it/0.1/dtd/'}
        root = etree.fromstring(self.fg.rss_str())
        filename = root.xpath('/rss/channel/item/torrent:filename/text()',
                              namespaces=ns)
        self.assertEqual(filename, ['file.xy'])
