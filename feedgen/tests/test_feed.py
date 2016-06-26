# -*- coding: utf-8 -*-

"""
Tests for a basic feed

These are test cases for a basic feed.
A basic feed does not contain entries so far.
"""

import unittest
from lxml import etree
from ..feed import Podcast
import feedgen.version

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):

        fg = Podcast()

        self.nsRss = "http://purl.org/rss/1.0/modules/content/"
        self.feedUrl = "http://example.com/feeds/myfeed.rss"

        self.title = 'Some Testfeed'

        self.authorName = 'John Doe'
        self.authorMail = 'john@example.de'

        self.linkHref = 'http://example.com'
        self.description = 'This is a cool feed!'

        self.language = 'en'

        self.cloudDomain = 'example.com'
        self.cloudPort = '4711'
        self.cloudPath = '/ws/example'
        self.cloudRegisterProcedure = 'registerProcedure'
        self.cloudProtocol = 'SOAP 1.1'

        self.contributor = {'name':"Contributor Name", 'email': 'Contributor email'}
        self.copyright = "The copyright notice"
        self.docs = 'http://www.rssboard.org/rss-specification'
        self.managingEditor = 'mail@example.com'
        self.skipDays = 'Tuesday'
        self.skipHours = 23

        self.programname = feedgen.version.name

        self.webMaster = 'webmaster@example.com'

        fg.name(self.title)
        fg.website(href=self.linkHref)
        fg.description(self.description)
        fg.language(self.language)
        fg.cloud(domain=self.cloudDomain, port=self.cloudPort,
                path=self.cloudPath, registerProcedure=self.cloudRegisterProcedure,
                protocol=self.cloudProtocol)
        fg.copyright(self.copyright)
        fg.managingEditor(self.managingEditor)
        fg.skipDays(self.skipDays)
        fg.skipHours(self.skipHours)
        fg.webMaster(self.webMaster)
        fg.feed_url(self.feedUrl)

        self.fg = fg


    def test_baseFeed(self):
        fg = self.fg

        assert fg.name() == self.title

        assert fg.managingEditor() == self.managingEditor
        assert fg.webMaster() == self.webMaster

        assert fg.website() == self.linkHref

        assert fg.description() == self.description

        assert fg.language() == self.language
        assert fg.feed_url() == self.feedUrl


    def test_rssFeedFile(self):
        fg = self.fg
        filename = 'tmp_Rssfeed.xml'
        fg.rss_file(filename=filename, xml_declaration=False)

        with open (filename, "r") as myfile:
            rssString=myfile.read().replace('\n', '')

        self.checkRssString(rssString)

    def test_rssFeedString(self):
        fg = self.fg
        rssString = fg.rss_str(xml_declaration=False)
        self.checkRssString(rssString)


    def checkRssString(self, rssString):

        feed = etree.fromstring(rssString)
        nsRss = self.nsRss
        nsAtom = "http://www.w3.org/2005/Atom"

        channel = feed.find("channel")
        assert channel != None

        assert channel.find("title").text == self.title
        assert channel.find("description").text == self.description
        assert channel.find("lastBuildDate").text != None
        assert channel.find("docs").text == "http://www.rssboard.org/rss-specification"
        assert self.programname in channel.find("generator").text
        assert channel.find("cloud").get('domain') == self.cloudDomain
        assert channel.find("cloud").get('port') == self.cloudPort
        assert channel.find("cloud").get('path') == self.cloudPath
        assert channel.find("cloud").get('registerProcedure') == self.cloudRegisterProcedure
        assert channel.find("cloud").get('protocol') == self.cloudProtocol
        assert channel.find("copyright").text == self.copyright
        assert channel.find("docs").text == self.docs
        assert channel.find("managingEditor").text == self.managingEditor
        assert channel.find("skipDays").find("day").text == self.skipDays
        assert int(channel.find("skipHours").find("hour").text) == self.skipHours
        assert channel.find("webMaster").text == self.webMaster
        assert channel.find("{%s}link" % nsAtom).get('href') == self.feedUrl
        assert channel.find("{%s}link" % nsAtom).get('rel') == 'self'
        assert channel.find("{%s}link" % nsAtom).get('type') == \
               'application/rss+xml'

    def test_feedUrlValidation(self):
        self.assertRaises(ValueError, self.fg.feed_url, "example.com/feed.rss")

    def test_generator(self):
        software_name = "My Awesome Software"
        self.fg.generator(software_name)
        rss = self.fg._create_rss()
        generator = rss.find("channel").find("generator").text
        assert software_name in generator
        assert self.programname in generator

        self.fg.generator(software_name, exclude_feedgen=True)
        generator = self.fg._create_rss().find("channel").find("generator").text
        assert software_name in generator
        assert self.programname not in generator


if __name__ == '__main__':
    unittest.main()
