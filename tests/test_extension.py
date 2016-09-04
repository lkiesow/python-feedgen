# -*- coding: utf-8 -*-

"""
Tests for extensions
"""

import unittest
from feedgen.feed import FeedGenerator
from lxml import etree


class TestExtensionSyndication(unittest.TestCase):

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('syndication')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_update_period(self):
        for period_type in ('hourly', 'daily', 'weekly',
                            'monthly', 'yearly'):
            self.fg.syndication.update_period(period_type)
            root = etree.fromstring(self.fg.rss_str())
            a = root.xpath('/rss/channel/sy:UpdatePeriod',
                           namespaces={
                               'sy':'http://purl.org/rss/1.0/modules/syndication/'
                           })
            assert a[0].text == period_type

    def test_update_frequency(self):
        for frequency in (1, 100, 2000, 100000):
            self.fg.syndication.update_frequency(frequency)
            root = etree.fromstring(self.fg.rss_str())
            a = root.xpath('/rss/channel/sy:UpdateFrequency',
                           namespaces={
                               'sy':'http://purl.org/rss/1.0/modules/syndication/'
                           })
            assert a[0].text == str(frequency)

    def test_update_base(self):
        base = '2000-01-01T12:00+00:00'
        self.fg.syndication.update_base(base)
        root = etree.fromstring(self.fg.rss_str())
        a = root.xpath('/rss/channel/sy:UpdateBase',
                       namespaces={
                               'sy':'http://purl.org/rss/1.0/modules/syndication/'
                           })
        assert a[0].text == base


class TestExtensionPodcast(unittest.TestCase):

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('podcast')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_category(self):
        self.fg.podcast.itunes_category('Technology', 'Podcasting')
        self.fg.podcast.itunes_explicit('no')
        self.fg.podcast.itunes_complete('no')
        self.fg.podcast.itunes_new_feed_url('http://example.com/new-feed.rss')
        self.fg.podcast.itunes_owner('John Doe', 'john@example.com')
        ns = {'itunes':'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        root = etree.fromstring(self.fg.rss_str())
        cat = root.xpath('/rss/channel/itunes:category/@text', namespaces=ns)
        scat = root.xpath('/rss/channel/itunes:category/itunes:category/@text',
              namespaces=ns)
        assert cat[0] == 'Technology'
        assert scat[0] == 'Podcasting'
