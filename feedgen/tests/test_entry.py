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

        fg.title(self.title)

        fe = fg.add_episode()
        fe.guid('http://lernfunk.de/media/654321/1')
        fe.title('The First Episode')

        #Use also the list directly
        fe = fg.episode_class()
        fg.episodes.append(fe)
        fe.guid('http://lernfunk.de/media/654321/1')
        fe.title('The Second Episode')

        fe = fg.add_episode()
        fe.guid('http://lernfunk.de/media/654321/1')
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
        fe.guid('http://lernfunk.de/media/654321/1')
        fe.title('The Third Episode')
        assert len(fg.episodes) == 1
        fg.episodes.pop(0)
        assert len(fg.episodes) == 0

    def test_removeEntryByEntry(self):
        fg = Podcast()
        self.feedId = 'http://example.com'
        self.title = 'Some Testfeed'

        fe = fg.add_episode()
        fe.guid('http://lernfunk.de/media/654321/1')
        fe.title('The Third Episode')

        assert len(fg.episodes) == 1
        fg.episodes.remove(fe)
        assert len(fg.episodes) == 0

    def test_categoryHasDomain(self):
        fg = Podcast()
        fg.title('some title')
        fg.link( href='http://www.dontcare.com')
        fg.description('description')
        fe = fg.add_episode()
        fe.guid('http://lernfunk.de/media/654321/1')
        fe.title('some title')
        fe.category([
             {'term' : 'category',
              'scheme': 'http://www.somedomain.com/category',
              }])

        result = fg.rss_str()
        assert b'domain="http://www.somedomain.com/category"' in result
