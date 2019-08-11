import unittest

from lxml import etree

from feedgen.feed import FeedGenerator


class TestExtensionMedia(unittest.TestCase):

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('media')
        self.fg.id('id')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_media_content(self):
        fe = self.fg.add_item()
        fe.id('id')
        fe.title('title')
        fe.content('content')
        fe.media.content(url='file1.xy')
        fe.media.content(url='file2.xy')
        fe.media.content(url='file1.xy', group=2)
        fe.media.content(url='file2.xy', group=2)
        fe.media.content(url='file.xy', group=None)

        ns = {'media': 'http://search.yahoo.com/mrss/',
              'a': 'http://www.w3.org/2005/Atom'}
        # Check that we have the item in the resulting RSS
        root = etree.fromstring(self.fg.rss_str())
        url = root.xpath('/rss/channel/item/media:group/media:content[1]/@url',
                         namespaces=ns)
        assert url == ['file1.xy', 'file1.xy']

        # There is one without a group
        url = root.xpath('/rss/channel/item/media:content[1]/@url',
                         namespaces=ns)
        assert url == ['file.xy']

        # Check that we have the item in the resulting Atom feed
        root = etree.fromstring(self.fg.atom_str())
        url = root.xpath('/a:feed/a:entry/media:group/media:content[1]/@url',
                         namespaces=ns)
        assert url == ['file1.xy', 'file1.xy']

        fe.media.content(content=[], replace=True)
        assert fe.media.content() == []

    def test_media_thumbnail(self):
        fe = self.fg.add_item()
        fe.id('id')
        fe.title('title')
        fe.content('content')
        fe.media.thumbnail(url='file1.xy')
        fe.media.thumbnail(url='file2.xy')
        fe.media.thumbnail(url='file1.xy', group=2)
        fe.media.thumbnail(url='file2.xy', group=2)
        fe.media.thumbnail(url='file.xy', group=None)

        ns = {'media': 'http://search.yahoo.com/mrss/',
              'a': 'http://www.w3.org/2005/Atom'}
        # Check that we have the item in the resulting RSS
        root = etree.fromstring(self.fg.rss_str())
        url = root.xpath(
                '/rss/channel/item/media:group/media:thumbnail[1]/@url',
                namespaces=ns)
        assert url == ['file1.xy', 'file1.xy']

        # There is one without a group
        url = root.xpath('/rss/channel/item/media:thumbnail[1]/@url',
                         namespaces=ns)
        assert url == ['file.xy']

        # Check that we have the item in the resulting Atom feed
        root = etree.fromstring(self.fg.atom_str())
        url = root.xpath('/a:feed/a:entry/media:group/media:thumbnail[1]/@url',
                         namespaces=ns)
        assert url == ['file1.xy', 'file1.xy']

        fe.media.thumbnail(thumbnail=[], replace=True)
        assert fe.media.thumbnail() == []
