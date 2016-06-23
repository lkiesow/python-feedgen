# -*- coding: utf-8 -*-

"""
Tests for a basic feed

These are test cases for a basic feed.
A basic feed does not contain entries so far.
"""

import unittest
from lxml import etree
from ..feed import FeedGenerator

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):

        fg = FeedGenerator()

        self.nsRss = "http://purl.org/rss/1.0/modules/content/"

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

        self.webMaster = 'webmaster@example.com'

        fg.title(self.title)
        fg.link( href=self.linkHref)
        fg.description(self.description)
        fg.language(self.language)
        fg.cloud(domain=self.cloudDomain, port=self.cloudPort,
                path=self.cloudPath, registerProcedure=self.cloudRegisterProcedure,
                protocol=self.cloudProtocol)
        fg.copyright(self.copyright)
        fg.docs(docs=self.docs)
        fg.managingEditor(self.managingEditor)
        fg.skipDays(self.skipDays)
        fg.skipHours(self.skipHours)
        fg.webMaster(self.webMaster)

        self.fg = fg


    def test_baseFeed(self):
        fg = self.fg

        assert fg.title() == self.title

        assert fg.managingEditor() == self.managingEditor
        assert fg.webMaster() == self.webMaster

        assert fg.link() == self.linkHref

        assert fg.description() == self.description

        assert fg.language() == self.language


    def test_rssFeedFile(self):
        fg = self.fg
        filename = 'tmp_Rssfeed.xml'
        fg.rss_file(filename=filename, pretty=True, xml_declaration=False)

        with open (filename, "r") as myfile:
            rssString=myfile.read().replace('\n', '')

        self.checkRssString(rssString)

    def test_rssFeedString(self):
        fg = self.fg
        rssString = fg.rss_str(pretty=True, xml_declaration=False)
        self.checkRssString(rssString)


    def checkRssString(self, rssString):

        feed = etree.fromstring(rssString)
        nsRss = self.nsRss

        channel = feed.find("channel")
        assert channel != None

        assert channel.find("title").text == self.title
        assert channel.find("description").text == self.description
        assert channel.find("lastBuildDate").text != None
        assert channel.find("docs").text == "http://www.rssboard.org/rss-specification"
        assert channel.find("generator").text == "python-feedgen"
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

if __name__ == '__main__':
    unittest.main()
