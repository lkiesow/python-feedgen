# -*- coding: utf-8 -*-

"""
Tests for a basic feed

These are test cases for a basic feed.
A basic feed does not contain entries so far.
"""

import unittest
from lxml import etree

from feedgen.person import Person
from feedgen.category import Category
from ..feed import Podcast
import feedgen.version
import datetime
import dateutil.tz
import dateutil.parser

class TestPodcast(unittest.TestCase):

    def setUp(self):

        fg = Podcast()

        self.nsContent = "http://purl.org/rss/1.0/modules/content/"
        self.nsDc = "http://purl.org/dc/elements/1.1/"
        self.nsItunes = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        self.feedUrl = "http://example.com/feeds/myfeed.rss"

        self.title = 'Some Testfeed'

        self.author = Person('John Doe', 'john@example.de')

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
        self.skipDays = 'Tuesday'
        self.skipHours = 23

        self.explicit = False

        self.programname = feedgen.version.name

        self.webMaster = Person(email='webmaster@example.com')

        fg.name(self.title)
        fg.website(href=self.linkHref)
        fg.description(self.description)
        fg.language(self.language)
        fg.cloud(domain=self.cloudDomain, port=self.cloudPort,
                path=self.cloudPath, registerProcedure=self.cloudRegisterProcedure,
                protocol=self.cloudProtocol)
        fg.copyright(self.copyright)
        fg.authors.append(self.author)
        fg.skip_days(self.skipDays)
        fg.skip_hours(self.skipHours)
        fg.web_master(self.webMaster)
        fg.feed_url(self.feedUrl)
        fg.explicit(self.explicit)

        self.fg = fg


    def test_baseFeed(self):
        fg = self.fg

        assert fg.name() == self.title

        assert fg.authors[0] == self.author
        assert fg.web_master() == self.webMaster

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
        nsRss = self.nsContent
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
        assert self.author.email in channel.find("managingEditor").text
        assert channel.find("skipDays").find("day").text == self.skipDays
        assert int(channel.find("skipHours").find("hour").text) == self.skipHours
        assert self.webMaster.email in channel.find("webMaster").text
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

    def test_str(self):
        assert str(self.fg) == self.fg.rss_str(
            minimize=False,
            encoding="UTF-8",
            xml_declaration=True
        )

    def test_updated(self):
        date = datetime.datetime(2016, 1, 1, 0, 10, tzinfo=dateutil.tz.tzutc())

        def getLastBuildDateElement(fg):
            return fg._create_rss().find("channel").find("lastBuildDate")

        # Test that it has a default
        assert getLastBuildDateElement(self.fg) is not None

        # Test that it respects my custom value
        self.fg.last_updated(date)
        lastBuildDate = getLastBuildDateElement(self.fg)
        assert lastBuildDate is not None
        assert dateutil.parser.parse(lastBuildDate.text) == date

        # Test that it is left out when set to False
        self.fg.last_updated(False)
        lastBuildDate = getLastBuildDateElement(self.fg)
        assert lastBuildDate is None

    def test_AuthorEmail(self):
        # Just email - so use managingEditor, not dc:creator or itunes:author
        # This is per the RSS best practices, see the section about dc:creator
        self.fg.authors = [Person(None, "justan@email.address")]
        channel = self.fg._create_rss().find("channel")
        # managingEditor uses email?
        assert channel.find("managingEditor").text == self.fg.authors[0].email
        # No dc:creator?
        assert channel.find("{%s}creator" % self.nsDc) is None
        # No itunes:author?
        assert channel.find("{%s}author" % self.nsItunes) is None

    def test_AuthorName(self):
        # Just name - use dc:creator and itunes:author, not managingEditor
        self.fg.authors = [Person("Just a. Name")]
        channel = self.fg._create_rss().find("channel")
        # No managingEditor?
        assert channel.find("managingEditor") is None
        # dc:creator equals name?
        assert channel.find("{%s}creator" % self.nsDc).text == \
               self.fg.authors[0].name
        # itunes:author equals name?
        assert channel.find("{%s}author" % self.nsItunes).text == \
            self.fg.authors[0].name

    def test_AuthorNameAndEmail(self):
        # Both name and email - use managingEditor and itunes:author,
        # not dc:creator
        self.fg.authors = [Person("Both a name", "and_an@email.com")]
        channel = self.fg._create_rss().find("channel")
        # Does managingEditor follow the pattern "email (name)"?
        self.assertEqual(self.fg.authors[0].email +
                         " (" + self.fg.authors[0].name + ")",
                         channel.find("managingEditor").text)
        # No dc:creator?
        assert channel.find("{%s}creator" % self.nsDc) is None
        # itunes:author uses name only?
        assert channel.find("{%s}author" % self.nsItunes).text == \
            self.fg.authors[0].name

    def test_multipleAuthors(self):
        # Multiple authors - use itunes:author and dc:creator, not
        # managingEditor.

        person1 = Person("Multiple", "authors@example.org")
        person2 = Person("Are", "cool@example.org")
        self.fg.authors = [person1, person2]
        channel = self.fg._create_rss().find("channel")

        # Test dc:creator
        author_elements = \
            channel.findall("{%s}creator" % self.nsDc)
        author_texts = [e.text for e in author_elements]

        assert len(author_texts) == 2
        assert person1.name in author_texts[0]
        assert person1.email in author_texts[0]
        assert person2.name in author_texts[1]
        assert person2.email in author_texts[1]

        # Test itunes:author
        itunes_author = channel.find("{%s}author" % self.nsItunes)
        assert itunes_author is not None
        itunes_author_text = itunes_author.text
        assert person1.name in itunes_author_text
        assert person1.email not in itunes_author_text
        assert person2.name in itunes_author_text
        assert person2.email not in itunes_author_text

        # Test that managingEditor is not used
        assert channel.find("managingEditor") is None

    def test_authorsInvalidValue(self):
        self.assertRaises(TypeError, self.do_authorsInvalidValue)

    def do_authorsInvalidValue(self):
        self.fg.authors = Person("Opsie", "forgot@list.org")


    def test_webMaster(self):
        self.fg.web_master(Person(None, "justan@email.address"))
        channel = self.fg._create_rss().find("channel")
        assert channel.find("webMaster").text == self.fg.web_master().email

        self.assertRaises(ValueError, self.fg.web_master,
                          Person("Mr. No Email Address"))

        self.fg.web_master(Person("Both a name", "and_an@email.com"))
        channel = self.fg._create_rss().find("channel")
        # Does webMaster follow the pattern "email (name)"?
        self.assertEqual(self.fg.web_master().email +
                         " (" + self.fg.web_master().name + ")",
                         channel.find("webMaster").text)

    def test_categoryWithoutSubcategory(self):
        c = Category("Arts")
        self.fg.category(c)
        channel = self.fg._create_rss().find("channel")
        itunes_category = channel.find("{%s}category" % self.nsItunes)
        assert itunes_category is not None

        self.assertEqual(itunes_category.get("text"), c.category)

        assert itunes_category.find("{%s}category" % self.nsItunes) is None

    def test_categoryWithSubcategory(self):
        c = Category("Arts", "Food")
        self.fg.category(c)
        channel = self.fg._create_rss().find("channel")
        itunes_category = channel.find("{%s}category" % self.nsItunes)
        assert itunes_category is not None
        itunes_subcategory = itunes_category\
            .find("{%s}category" % self.nsItunes)
        assert itunes_subcategory is not None
        self.assertEqual(itunes_subcategory.get("text"), c.subcategory)

    def test_categoryChecks(self):
        c = ("Arts", "Food")
        self.assertRaises(TypeError, self.fg.category, c)

    def test_explicitIsExplicit(self):
        self.fg.explicit(True)
        channel = self.fg._create_rss().find("channel")
        itunes_explicit = channel.find("{%s}explicit" % self.nsItunes)
        assert itunes_explicit is not None
        assert itunes_explicit.text.lower() in ("yes", "explicit", "true"),\
            "itunes:explicit was %s, expected yes, explicit or true" \
            % itunes_explicit.text

    def test_explicitIsClean(self):
        self.fg.explicit(False)
        channel = self.fg._create_rss().find("channel")
        itunes_explicit = channel.find("{%s}explicit" % self.nsItunes)
        assert itunes_explicit is not None
        assert itunes_explicit.text.lower() in ("no", "clean", "false"),\
            "itunes:explicit was %s, expected no, clean or false" \
            % itunes_explicit.text

    def test_mandatoryValues(self):
        # Try to create a Podcast once for each mandatory property.
        # On each iteration, exactly one of the properties is not set.
        # Therefore, an exception should be thrown on each iteration.
        mandatory_properties = {
            "description",
            "title",
            "link",
            "explicit",
        }

        for test_property in mandatory_properties:
            fg = Podcast()
            if test_property != "description":
                fg.description(self.description)
            if test_property != "title":
                fg.name(self.title)
            if test_property != "link":
                fg.website(self.linkHref)
            if test_property != "explicit":
                fg.explicit(self.explicit)
            try:
                self.assertRaises(ValueError, fg._create_rss)
            except AssertionError as e:
                raise AssertionError("The test failed for %s" % test_property)\
                    from e

if __name__ == '__main__':
    unittest.main()
