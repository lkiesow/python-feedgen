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
        assert fe.torrent.filename() == 'file.xy'
        assert fe.torrent.infohash() == '123'
        assert fe.torrent.contentlength() == '23'
        assert fe.torrent.seeds() == '1'
        assert fe.torrent.peers() == '2'
        assert fe.torrent.verified() == '1'

        # Check that we have the item in the resulting XML
        ns = {'torrent': 'http://xmlns.ezrss.it/0.1/dtd/'}
        root = etree.fromstring(self.fg.rss_str())
        filename = root.xpath('/rss/channel/item/torrent:filename/text()',
                              namespaces=ns)
        assert filename == ['file.xy']
