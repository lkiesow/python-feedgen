# -*- coding: utf-8 -*-

"""
Tests for a basic feed

These test cases contain test cases for a basic feed. A basic feed does not contain entries so far.
"""

import unittest
from lxml import etree

class TestSequenceFunctions(unittest.TestCase):

	def setUp(self):
		from feedgen.feed import FeedGenerator
		fg = FeedGenerator()

		self.feedId = 'http://lernfunk.de/media/654321'
		self.title = 'Some Testfeed'
		
		self.authorName = 'John Doe'
		self.authorMail = 'john@example.de'
		self.author = {'name': self.authorName,'email': self.authorMail}

		self.linkHref = 'http://example.com'
		self.linkRel = 'alternate'

		self.logo = 'http://ex.com/logo.jpg'
		self.subtitle = 'This is a cool feed!'

		self.link2Href = 'http://larskiesow.de/test.atom'
		self.link2Rel = 'self'

		self.language = 'en'

		fg.id(self.feedId)
		fg.title(self.title)
		fg.author(self.author)
		fg.link( href=self.linkHref, rel=self.linkRel )
		fg.logo(self.logo)
		fg.subtitle(self.subtitle)
		fg.link( href=self.link2Href, rel=self.link2Rel )
		fg.language(self.language)

		self.fg = fg

	def test_baseFeed(self):
		fg = self.fg

		assert fg.id() == self.feedId
		assert fg.title() == self.title

		assert fg.author()[0]['name'] == self.authorName
		assert fg.author()[0]['email'] == self.authorMail

		assert fg.link()[0]['href'] == self.linkHref
		assert fg.link()[0]['rel'] == self.linkRel

		assert fg.logo() == self.logo
		assert fg.subtitle() == self.subtitle

		assert fg.link()[1]['href'] == self.link2Href
		assert fg.link()[1]['rel'] == self.link2Rel

		assert fg.language() == self.language

	def test_atomFeed(self):
		fg = self.fg

		atomString = fg.atom_str(pretty=True)
		feed = etree.fromstring(atomString)

		nsAtom = "http://www.w3.org/2005/Atom"

		assert feed.find("{%s}title" % nsAtom).text == self.title
		assert feed.find("{%s}updated" % nsAtom).text != None
		assert feed.find("{%s}id" % nsAtom).text == self.feedId
		
		assert feed.find("{%s}author" % nsAtom).find("{%s}name" % nsAtom).text == self.authorName
		assert feed.find("{%s}author" % nsAtom).find("{%s}email" % nsAtom).text == self.authorMail

		assert feed.findall("{%s}link" % nsAtom)[0].get('href') == self.linkHref
		assert feed.findall("{%s}link" % nsAtom)[0].get('rel') == self.linkRel
		assert feed.findall("{%s}link" % nsAtom)[1].get('href') == self.link2Href
		assert feed.findall("{%s}link" % nsAtom)[1].get('rel') == self.link2Rel
		
		assert feed.find("{%s}logo" % nsAtom).text == self.logo
		assert feed.find("{%s}subtitle" % nsAtom).text == self.subtitle

	def test_rssFeed(self):
		fg = self.fg
		
		rssString = fg.rss_str(pretty=True)
		feed = etree.fromstring(rssString)

		nsAtom = "http://www.w3.org/2005/Atom"
		nsRss = "http://purl.org/rss/1.0/modules/content/"

		channel = feed.find("channel")
		assert channel != None

		assert channel.find("title").text == self.title
		assert channel.find("description").text == self.subtitle
		assert channel.find("lastBuildDate").text != None
		assert channel.find("docs").text == "http://www.rssboard.org/rss-specification"
		assert channel.find("generator").text == "python-feedgen"

		assert channel.findall("{%s}link" % nsAtom)[0].get('href') == self.link2Href
		assert channel.findall("{%s}link" % nsAtom)[0].get('rel') == self.link2Rel
		
		assert channel.find("image").find("url").text == self.logo
		assert channel.find("image").find("title").text == self.title
		assert channel.find("image").find("link").text == self.link2Href

if __name__ == '__main__':
    unittest.main()