# -*- coding: utf-8 -*-

"""
Tests for a basic entry

These are test cases for a basic entry.
"""

import unittest
from lxml import etree
from ..feed import FeedGenerator

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

	def test_categoryHasDomain(self):
		fg = FeedGenerator()
		fg.title('some title')
		fg.link( href='http://www.dontcare.com', rel='alternate' )
		fg.description('description')
		fe = fg.add_entry()
		fe.id('http://lernfunk.de/media/654321/1')
		fe.title('some title')
		fe.category([
			 {'term' : 'category',
			  'scheme': 'http://www.somedomain.com/category',
			  'label' : 'Category',
			  }])

		result = fg.rss_str()
		assert b'domain="http://www.somedomain.com/category"' in result
		
	def test_content_cdata_type(self):
		fg = FeedGenerator()
		fg.title('some title')
		fg.id('http://lernfunk.de/media/654322/1')
		fe = fg.add_entry()
		fe.id('http://lernfunk.de/media/654322/1')
		fe.title('some title')
		fe.content('content', type='CDATA')
		result = fg.atom_str()
		assert b'<content type="CDATA"><![CDATA[content]]></content>' in result

