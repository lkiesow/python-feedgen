# -*- coding: utf-8 -*-

"""
Tests for a basic feed

These test cases contain test cases for a basic feed. A basic feed does not contain entries so far.
"""

import unittest
from lxml import etree
from feedgen.feed import FeedGenerator


class TestSequenceFunctions(unittest.TestCase):

	def setUp(self):
		
		fg = FeedGenerator()
		self.feedId = 'http://example.com'
		self.title = 'Some Testfeed'

		fg.id(self.feedId)
		fg.title(self.title)

		fe = fg.add_entry()
		fe.id('http://lernfunk.de/media/654321/1')
		fe.title('The First Episode')

		#Use also the different name add_item
		fe = fg.add_item()
		fe.id('http://lernfunk.de/media/654321/1')
		fe.title('The Second Episode')

		fe = fg.add_entry()
		fe.id('http://lernfunk.de/media/654321/1')
		fe.title('The Third Episode')

		self.fg = fg

	def test_checkEntryNumbers(self):

		fg = self.fg
		assert len(fg.entry()) == 3

	def test_checkItemNumbers(self):

		fg = self.fg
		assert len(fg.item()) == 3

	def test_checkEntryContent(self):

		fg = self.fg
		assert len(fg.entry()) != None

	def test_removeEntryByIndex(self):
		fg = FeedGenerator()
		self.feedId = 'http://example.com'
		self.title = 'Some Testfeed'

		fe = fg.add_entry()
		fe.id('http://lernfunk.de/media/654321/1')
		fe.title('The Third Episode')
		assert len(fg.entry()) == 1
		fg.remove_entry(0)
		assert len(fg.entry()) == 0

	def test_removeEntryByEntry(self):
		fg = FeedGenerator()
		self.feedId = 'http://example.com'
		self.title = 'Some Testfeed'

		fe = fg.add_entry()
		fe.id('http://lernfunk.de/media/654321/1')
		fe.title('The Third Episode')
		
		assert len(fg.entry()) == 1
		fg.remove_entry(fe)
		assert len(fg.entry()) == 0
		




