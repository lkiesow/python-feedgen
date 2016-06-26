# -*- coding: utf-8 -*-

"""
Tests for a basic entry

These are test cases for a basic entry.
"""

import unittest
from lxml import etree
from ..feed import Podcast

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):

        fg = Podcast()
        self.title = 'Some Testfeed'

        fg.name(self.title)

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
