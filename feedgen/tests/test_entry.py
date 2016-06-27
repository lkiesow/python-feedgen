# -*- coding: utf-8 -*-

"""
Tests for a basic entry

These are test cases for a basic entry.
"""

import unittest
from lxml import etree
from ..feed import Podcast
import datetime
import pytz
from dateutil.parser import parse as parsedate

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):

        fg = Podcast()
        self.title = 'Some Testfeed'
        self.link = 'http://lernfunk.de'
        self.description = 'A cool tent'

        fg.name(self.title)
        fg.website(self.link)
        fg.description(self.description)

        fe = fg.add_episode()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The First Episode')

        #Use also the list directly
        fe = fg.Episode()
        fg.episodes.append(fe)
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Second Episode')

        fe = fg.add_episode()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Third Episode')

        self.fg = fg

    def test_checkEntryNumbers(self):

        fg = self.fg
        assert len(fg.episodes) == 3

    def test_checkItemNumbers(self):

        fg = self.fg
        assert len(fg.episodes) == 3

    def test_checkEntryContent(self):

        fg = self.fg
        assert len(fg.episodes) is not None

    def test_removeEntryByIndex(self):
        fg = Podcast()
        self.feedId = 'http://example.com'
        self.title = 'Some Testfeed'

        fe = fg.add_episode()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Third BaseEpisode')
        assert len(fg.episodes) == 1
        fg.episodes.pop(0)
        assert len(fg.episodes) == 0

    def test_removeEntryByEntry(self):
        fg = Podcast()
        self.feedId = 'http://example.com'
        self.title = 'Some Testfeed'

        fe = fg.add_episode()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Third BaseEpisode')

        assert len(fg.episodes) == 1
        fg.episodes.remove(fe)
        assert len(fg.episodes) == 0

    def test_idIsSet(self):
        guid = "http://example.com/podcast/episode1"
        episode = self.fg.Episode()
        episode.title("My first episode")
        episode.id(guid)
        item = episode.rss_entry()

        assert item.find("guid").text == guid

    def test_idNotSetButEnclosureIsUsed(self):
        guid = "http://example.com/podcast/episode1.mp3"
        episode = self.fg.Episode()
        episode.title("My first episode")
        episode.enclosure(guid, 0, "audio/mpeg")

        item = episode.rss_entry()
        assert item.find("guid").text == guid

    def test_idSetToFalseSoEnclosureNotUsed(self):
        episode = self.fg.Episode()
        episode.title("My first episode")
        episode.enclosure("http://example.com/podcast/episode1.mp3", 0, "audio/mpeg")
        episode.id(False)

        item = episode.rss_entry()
        assert item.find("guid") is None

    def test_feedPubDateUsesNewestEpisode(self):
        self.fg.episodes[0].published(
            datetime.datetime(2015, 1, 1, 15, 0, tzinfo=pytz.utc)
        )
        self.fg.episodes[1].published(
            datetime.datetime(2016, 1, 3, 12, 22, tzinfo=pytz.utc)
        )
        self.fg.episodes[2].published(
            datetime.datetime(2014, 3, 2, 13, 11, tzinfo=pytz.utc)
        )
        rss = self.fg._create_rss()
        pubDate = rss.find("channel").find("pubDate")
        assert pubDate is not None
        parsedPubDate = parsedate(pubDate.text)
        assert parsedPubDate == self.fg.episodes[1].published()

    def test_feedPubDateNotOverriddenByEpisode(self):
        self.fg.episodes[0].published(
            datetime.datetime(2015, 1, 1, 15, 0, tzinfo=pytz.utc)
        )
        pubDate = self.fg._create_rss().find("channel").find("pubDate")
        # Now it uses the episode's published date
        assert pubDate is not None
        assert parsedate(pubDate.text) == self.fg.episodes[0].published()

        new_date = datetime.datetime(2016, 1, 2, 3, 4, tzinfo=pytz.utc)
        self.fg.published(new_date)
        pubDate = self.fg._create_rss().find("channel").find("pubDate")
        # Now it uses the custom-set date
        assert pubDate is not None
        assert parsedate(pubDate.text) == new_date

    def test_feedPubDateDisabled(self):
        self.fg.episodes[0].published(
            datetime.datetime(2015, 1, 1, 15, 0, tzinfo=pytz.utc)
        )
        self.fg.published(False)
        pubDate = self.fg._create_rss().find("channel").find("pubDate")
        assert pubDate is None  # Not found!
