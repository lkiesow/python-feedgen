# -*- coding: utf-8 -*-

"""
Tests for extensions
"""

import unittest
from feedgen.feed import FeedGenerator
from lxml import etree


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


class TestExtensionPodcast(unittest.TestCase):

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('podcast')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_category_new(self):
        self.fg.podcast.itunes_category([{'cat': 'Technology',
                                          'sub': 'Podcasting'}])
        self.fg.podcast.itunes_explicit('no')
        self.fg.podcast.itunes_complete('no')
        self.fg.podcast.itunes_new_feed_url('http://example.com/new-feed.rss')
        self.fg.podcast.itunes_owner('John Doe', 'john@example.com')
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        root = etree.fromstring(self.fg.rss_str())
        cat = root.xpath('/rss/channel/itunes:category/@text', namespaces=ns)
        scat = root.xpath('/rss/channel/itunes:category/itunes:category/@text',
                          namespaces=ns)
        assert cat[0] == 'Technology'
        assert scat[0] == 'Podcasting'

    def test_category(self):
        self.fg.podcast.itunes_category('Technology', 'Podcasting')
        self.fg.podcast.itunes_explicit('no')
        self.fg.podcast.itunes_complete('no')
        self.fg.podcast.itunes_new_feed_url('http://example.com/new-feed.rss')
        self.fg.podcast.itunes_owner('John Doe', 'john@example.com')
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        root = etree.fromstring(self.fg.rss_str())
        cat = root.xpath('/rss/channel/itunes:category/@text', namespaces=ns)
        scat = root.xpath('/rss/channel/itunes:category/itunes:category/@text',
                          namespaces=ns)
        assert cat[0] == 'Technology'
        assert scat[0] == 'Podcasting'

    def test_podcastItems(self):
        fg = self.fg
        fg.podcast.itunes_author('Lars Kiesow')
        fg.podcast.itunes_block('x')
        fg.podcast.itunes_complete(False)
        fg.podcast.itunes_explicit('no')
        fg.podcast.itunes_image('x.png')
        fg.podcast.itunes_subtitle('x')
        fg.podcast.itunes_summary('x')
        assert fg.podcast.itunes_author() == 'Lars Kiesow'
        assert fg.podcast.itunes_block() == 'x'
        assert fg.podcast.itunes_complete() == 'no'
        assert fg.podcast.itunes_explicit() == 'no'
        assert fg.podcast.itunes_image() == 'x.png'
        assert fg.podcast.itunes_subtitle() == 'x'
        assert fg.podcast.itunes_summary() == 'x'

        # Check that we have the item in the resulting XML
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        root = etree.fromstring(self.fg.rss_str())
        author = root.xpath('/rss/channel/itunes:author/text()', namespaces=ns)
        assert author == ['Lars Kiesow']

    def test_podcastEntryItems(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.podcast.itunes_author('Lars Kiesow')
        fe.podcast.itunes_block('x')
        fe.podcast.itunes_duration('00:01:30')
        fe.podcast.itunes_explicit('no')
        fe.podcast.itunes_image('x.png')
        fe.podcast.itunes_is_closed_captioned('yes')
        fe.podcast.itunes_order(1)
        fe.podcast.itunes_subtitle('x')
        fe.podcast.itunes_summary('x')
        assert fe.podcast.itunes_author() == 'Lars Kiesow'
        assert fe.podcast.itunes_block() == 'x'
        assert fe.podcast.itunes_duration() == '00:01:30'
        assert fe.podcast.itunes_explicit() == 'no'
        assert fe.podcast.itunes_image() == 'x.png'
        assert fe.podcast.itunes_is_closed_captioned()
        assert fe.podcast.itunes_order() == 1
        assert fe.podcast.itunes_subtitle() == 'x'
        assert fe.podcast.itunes_summary() == 'x'

        # Check that we have the item in the resulting XML
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        root = etree.fromstring(self.fg.rss_str())
        author = root.xpath('/rss/channel/item/itunes:author/text()',
                            namespaces=ns)
        assert author == ['Lars Kiesow']


class TestExtensionDc(unittest.TestCase):

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('dc')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_entryLoadExtension(self):
        fe = self.fg.add_item()
        try:
            fe.load_extension('dc')
        except ImportError:
            pass  # Extension already loaded

    def test_elements(self):
        for method in dir(self.fg.dc):
            if method.startswith('dc_'):
                m = getattr(self.fg.dc, method)
                m(method)
                assert m() == [method]

        self.fg.id('123')
        assert self.fg.atom_str()
        assert self.fg.rss_str()


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
