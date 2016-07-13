# -*- coding: utf-8 -*-
"""
    podgen.tests.test_podcast
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Test the Podcast alone, without any Episode objects.

    :copyright: 2016, Thorben Dahl <thorben@sjostrom.no>
    :license: FreeBSD and LGPL, see license.* for more details.
"""

import unittest
from lxml import etree
import tempfile
import os

from podgen import Person, Category, Podcast
import podgen.version
import datetime
import dateutil.tz
import dateutil.parser

class TestPodcast(unittest.TestCase):

    def setUp(self):

        fg = Podcast()

        self.nsContent = "http://purl.org/rss/1.0/modules/content/"
        self.nsDc = "http://purl.org/dc/elements/1.1/"
        self.nsItunes = "http://www.itunes.com/dtds/podcast-1.0.dtd"
        self.feed_url = "http://example.com/feeds/myfeed.rss"

        self.name = 'Some Testfeed'

        self.author = Person('John Doe', 'john@example.de')

        self.website = 'http://example.com'
        self.description = 'This is a cool feed!'
        self.subtitle = 'Coolest of all'

        self.language = 'en'

        self.cloudDomain = 'example.com'
        self.cloudPort = '4711'
        self.cloudPath = '/ws/example'
        self.cloudRegisterProcedure = 'registerProcedure'
        self.cloudProtocol = 'SOAP 1.1'

        self.pubsubhubbub = "http://pubsubhubbub.example.com/"

        self.contributor = {'name':"Contributor Name",
                            'email': 'Contributor email'}
        self.copyright = "The copyright notice"
        self.docs = 'http://www.rssboard.org/rss-specification'
        self.skip_days = {'Tuesday'}
        self.skip_hours = {23}

        self.explicit = False

        self.programname = podgen.version.name

        self.web_master = Person(email='webmaster@example.com')
        self.image = "http://example.com/static/podcast.png"
        self.owner = self.author
        self.complete = True
        self.new_feed_url = "https://example.com/feeds/myfeed2.rss"
        self.xslt = "http://example.com/feed/stylesheet.xsl"


        fg.name = self.name
        fg.website = self.website
        fg.description = self.description
        fg.subtitle = self.subtitle
        fg.language = self.language
        fg.cloud = (self.cloudDomain, self.cloudPort, self.cloudPath,
                    self.cloudRegisterProcedure, self.cloudProtocol)
        fg.pubsubhubbub = self.pubsubhubbub
        fg.copyright = self.copyright
        fg.authors.append(self.author)
        fg.skip_days = self.skip_days
        fg.skip_hours = self.skip_hours
        fg.web_master = self.web_master
        fg.feed_url = self.feed_url
        fg.explicit = self.explicit
        fg.image = self.image
        fg.owner = self.owner
        fg.complete = self.complete
        fg.new_feed_url = self.new_feed_url
        fg.xslt = self.xslt

        self.fg = fg

    def test_constructor(self):
        # Overwrite fg from setup
        self.fg = Podcast(
            name=self.name,
            website=self.website,
            description=self.description,
            subtitle=self.subtitle,
            language=self.language,
            cloud=(self.cloudDomain, self.cloudPort, self.cloudPath,
                   self.cloudRegisterProcedure, self.cloudProtocol),
            pubsubhubbub=self.pubsubhubbub,
            copyright=self.copyright,
            authors=[self.author],
            skip_days=self.skip_days,
            skip_hours=self.skip_hours,
            web_master=self.web_master,
            feed_url=self.feed_url,
            explicit=self.explicit,
            image=self.image,
            owner=self.owner,
            complete=self.complete,
            new_feed_url=self.new_feed_url,
            xslt=self.xslt,
        )
        # Test that the fields are actually set
        self.test_baseFeed()

    def test_constructorUnknownAttributes(self):
        self.assertRaises(TypeError, Podcast, naem="Oh, looks like a typo")
        self.assertRaises(TypeError, Podcast, "Haha, No Keyword")

    def test_baseFeed(self):
        fg = self.fg

        assert fg.name == self.name

        assert fg.authors[0] == self.author
        assert fg.web_master == self.web_master

        assert fg.website == self.website

        assert fg.description == self.description
        assert fg.subtitle == self.subtitle

        assert fg.language == self.language
        assert fg.feed_url == self.feed_url
        assert fg.image == self.image
        assert fg.owner == self.owner
        assert fg.complete == self.complete
        assert fg.pubsubhubbub == self.pubsubhubbub
        assert fg.cloud == (self.cloudDomain, self.cloudPort, self.cloudPath,
                            self.cloudRegisterProcedure, self.cloudProtocol)
        assert fg.copyright == self.copyright
        assert fg.new_feed_url == self.new_feed_url
        assert fg.skip_days == self.skip_days
        assert fg.skip_hours == self.skip_hours
        assert fg.xslt == self.xslt

    def test_rssFeedFile(self):
        fg = self.fg
        rssString = self.getRssFeedFileContents(fg, xml_declaration=False)\
            .replace('\n', '')
        self.checkRssString(rssString)

    def getRssFeedFileContents(self, fg, **kwargs):
        # Keep track of our temporary file and its filename
        filename = None
        file = None
        try:
            # Get our temporary file name
            file = tempfile.NamedTemporaryFile(delete=False)
            filename = file.name
            # Close the file; we will just use its name
            file.close()
            # Write the RSS to the file (overwriting it)
            fg.rss_file(filename=filename, **kwargs)
            # Read the resulting RSS
            with open(filename, "r") as myfile:
                rssString = myfile.read()
        finally:
            # We don't need the file any longer, so delete it
            if filename:
                os.unlink(filename)
            elif file:
                # Ops, we were interrupted between the first and second stmt
                filename = file.name
                file.close()
                os.unlink(filename)
            else:
                # We were interrupted between entering the try-block and
                # getting the temporary file. Not much we can do.
                pass
        return rssString


    def test_rssFeedString(self):
        fg = self.fg
        rssString = fg.rss_str(xml_declaration=False)
        self.checkRssString(rssString)

    def test_rssStringAndFileAreEqual(self):
        rss_string = self.fg.rss_str()
        rss_file = self.getRssFeedFileContents(self.fg)
        self.assertEqual(rss_string, rss_file)

    def checkRssString(self, rssString):
        feed = etree.fromstring(rssString)
        nsRss = self.nsContent
        nsAtom = "http://www.w3.org/2005/Atom"

        channel = feed.find("channel")
        assert channel != None

        assert channel.find("title").text == self.name
        assert channel.find("description").text == self.description
        assert channel.find("{%s}subtitle" % self.nsItunes).text == \
            self.subtitle
        assert channel.find("link").text == self.website
        assert channel.find("lastBuildDate").text != None
        assert channel.find("language").text == self.language
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
        assert channel.find("skipDays").find("day").text in self.skip_days
        assert int(channel.find("skipHours").find("hour").text) in self.skip_hours
        assert self.web_master.email in channel.find("webMaster").text

        links = channel.findall("{%s}link" % nsAtom)
        selflinks = [link for link in links if link.get('rel') == 'self']
        hublinks = [link for link in links if link.get('rel') == 'hub']

        assert selflinks, "No <atom:link rel='self'> element found"
        selflink = selflinks[0]
        assert selflink.get('href') == self.feed_url
        assert selflink.get('type') == 'application/rss+xml'

        assert hublinks, "No <atom:link rel='hub'> element found"
        hublink = hublinks[0]
        assert hublink.get('href') == self.pubsubhubbub
        assert hublink.get('type') is None

        assert channel.find("{%s}image" % self.nsItunes).get('href') == \
            self.image
        owner = channel.find("{%s}owner" % self.nsItunes)
        assert owner.find("{%s}name" % self.nsItunes).text == self.owner.name
        assert owner.find("{%s}email" % self.nsItunes).text == self.owner.email
        assert channel.find("{%s}complete" % self.nsItunes).text.lower() == \
            "yes"
        assert channel.find("{%s}new-feed-url" % self.nsItunes).text == \
            self.new_feed_url

    def test_feedUrlValidation(self):
        self.assertRaises(ValueError, setattr, self.fg, "feed_url",
                          "example.com/feed.rss")

    def test_generator(self):
        software_name = "My Awesome Software"
        software_version = (1, 0)
        software_url = "http://example.com/awesomesoft/"

        # Using set_generator, text includes python-podgen
        self.fg.set_generator(software_name)
        rss = self.fg._create_rss()
        generator = rss.find("channel").find("generator").text
        assert software_name in generator
        assert self.programname in generator

        # Using set_generator, text excludes python-podgen
        self.fg.set_generator(software_name, exclude_podgen=True)
        generator = self.fg._create_rss().find("channel").find("generator").text
        assert software_name in generator
        assert self.programname not in generator

        # Using set_generator, text includes name, version and url
        self.fg.set_generator(software_name, software_version, software_url)
        generator = self.fg._create_rss().find("channel").find("generator").text
        assert software_name in generator
        assert str(software_version[0]) in generator
        assert str(software_version[1]) in generator
        assert software_url in generator

        # Using generator directly, text excludes python-podgen
        self.fg.generator = software_name
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
        self.fg.last_updated = date
        lastBuildDate = getLastBuildDateElement(self.fg)
        assert lastBuildDate is not None
        assert dateutil.parser.parse(lastBuildDate.text) == date

        # Test that it is left out when set to False
        self.fg.last_updated = False
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
        self.fg.web_master = Person(None, "justan@email.address")
        channel = self.fg._create_rss().find("channel")
        assert channel.find("webMaster").text == self.fg.web_master.email

        self.assertRaises(ValueError, setattr, self.fg, "web_master",
                          Person("Mr. No Email Address"))

        self.fg.web_master = Person("Both a name", "and_an@email.com")
        channel = self.fg._create_rss().find("channel")
        # Does webMaster follow the pattern "email (name)"?
        self.assertEqual(self.fg.web_master.email +
                         " (" + self.fg.web_master.name + ")",
                         channel.find("webMaster").text)

    def test_categoryWithoutSubcategory(self):
        c = Category("Arts")
        self.fg.category = c
        channel = self.fg._create_rss().find("channel")
        itunes_category = channel.find("{%s}category" % self.nsItunes)
        assert itunes_category is not None

        self.assertEqual(itunes_category.get("text"), c.category)

        assert itunes_category.find("{%s}category" % self.nsItunes) is None

    def test_categoryWithSubcategory(self):
        c = Category("Arts", "Food")
        self.fg.category = c
        channel = self.fg._create_rss().find("channel")
        itunes_category = channel.find("{%s}category" % self.nsItunes)
        assert itunes_category is not None
        itunes_subcategory = itunes_category\
            .find("{%s}category" % self.nsItunes)
        assert itunes_subcategory is not None
        self.assertEqual(itunes_subcategory.get("text"), c.subcategory)

    def test_categoryChecks(self):
        c = ("Arts", "Food")
        self.assertRaises(TypeError, setattr, self.fg, "category", c)

    def test_explicitIsExplicit(self):
        self.fg.explicit = True
        channel = self.fg._create_rss().find("channel")
        itunes_explicit = channel.find("{%s}explicit" % self.nsItunes)
        assert itunes_explicit is not None
        assert itunes_explicit.text.lower() in ("yes", "explicit", "true"),\
            "itunes:explicit was %s, expected yes, explicit or true" \
            % itunes_explicit.text

    def test_explicitIsClean(self):
        self.fg.explicit = False
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
                fg.description = self.description
            if test_property != "title":
                fg.name = self.name
            if test_property != "link":
                fg.website = self.website
            if test_property != "explicit":
                fg.explicit = self.explicit
            try:
                self.assertRaises(ValueError, fg._create_rss)
            except AssertionError as e:
                raise AssertionError("The test failed for %s" % test_property)\
                    from e

    def test_withholdFromItunesOffByDefault(self):
        assert not self.fg.withhold_from_itunes

    def test_withholdFromItunes(self):
        self.fg.withhold_from_itunes = True
        itunes_block = self.fg._create_rss().find("channel")\
            .find("{%s}block" % self.nsItunes)
        assert itunes_block is not None
        self.assertEqual(itunes_block.text.lower(), "yes")

        self.fg.withhold_from_itunes = False
        itunes_block = self.fg._create_rss().find("channel")\
            .find("{%s}block" % self.nsItunes)
        assert itunes_block is None

    def test_modifyingSkipDaysAfterwards(self):
        self.fg.skip_days.add("Unrecognized day")
        self.assertRaises(ValueError, self.fg.rss_str)
        self.fg.skip_days.remove("Unrecognized day")
        self.fg.rss_str()  # Now it works

    def test_modifyingSkipHoursAfterwards(self):
        self.fg.skip_hours.add(26)
        self.assertRaises(ValueError, self.fg.rss_str)
        self.fg.skip_hours.remove(26)
        self.fg.rss_str()  # Now it works

    # Tests for xslt
    def test_xslt_str(self):
        def use_str(**kwargs):
            return self.fg.rss_str(**kwargs)
        self.help_test_xslt_using(use_str)

    def test_xslt_file(self):
        def use_file(**kwargs):
            return self.getRssFeedFileContents(self.fg, **kwargs)
        self.help_test_xslt_using(use_file)

    def help_test_xslt_using(self, generated_feed):
        """Run tests for xslt, generating the feed str using the given function.
        """
        xslt_path = "http://example.com/mystylesheet.xsl"
        xslt_pi = "<?xml-stylesheet"

        # No xslt when set to None
        self.fg.xslt = None
        assert xslt_pi not in generated_feed()
        assert xslt_pi not in generated_feed(minimize=True)
        assert xslt_pi not in generated_feed(xml_declaration=False)

        self.fg.xslt = xslt_path

        # Now we have the stylesheet in there
        assert xslt_pi in generated_feed()
        assert xslt_pi in generated_feed(minimize=True)
        assert xslt_pi in generated_feed(xml_declaration=False)

        assert xslt_path in generated_feed()
        assert xslt_path in generated_feed(minimize=True)
        assert xslt_path in generated_feed(xml_declaration=False)

    # Test for notifying a PubSubHubbub
    def test_notifyHub(self):
        url_hub = self.pubsubhubbub
        url_feed = self.feed_url
        assertEqual = self.assertEqual
        wanted_timeout = None

        class MyLittleRequests(object):
            @staticmethod
            def post(url, data, timeout, *args, **kwargs):
                assertEqual(url_hub, url)
                if wanted_timeout:
                    # Test that the timeout is equal what we put in
                    assertEqual(wanted_timeout, timeout)
                else:
                    # Test that the default timeout is OK
                    assert 2.0 < timeout < 10.0, "Too long or short timeout!"

                if isinstance(data, dict):
                    assert "hub.mode" in data
                    assertEqual("publish", data['hub.mode'])

                    assert "hub.url" in data
                    assertEqual(url_feed, data['hub.url'])

                else:
                    assert ("hub.mode", "publish") in data, \
                        "Pair (hub.mode, publish) not in %s" % data
                    assert ("hub.url", url_feed) in data, \
                        "Pair (hub.url, %s) not in %s" % (url_feed, data)

                class MyLittleResponse(object):
                    def raise_for_status(self):
                        pass
                return MyLittleResponse()

        self.fg.notify_hub(MyLittleRequests)
        # Test that the timeout parameter is given to requests
        wanted_timeout = 50.0
        self.fg.notify_hub(MyLittleRequests, wanted_timeout)

    def test_notifyHubMultiple(self):
        url_hub = self.pubsubhubbub
        url_other_hub = "https://pubsubhubbub.example.org"
        feeds = [Podcast(
            name="Test1",
            description="Testing a podcast",
            website="http://example.com",
            explicit=False,
            feed_url="http://example.com/feed1.rss",
            pubsubhubbub=self.pubsubhubbub),
                Podcast(
            name="Test2",
            description="Testing another podcast",
            website="http://example.com",
            explicit=True,
            feed_url="http://example.com/feed2.rss",
            pubsubhubbub=self.pubsubhubbub),
                self.fg
                ]

        assertEqual = self.assertEqual
        wanted_timeout = None

        class MyLittleRequests(object):
            num_feeds = 0
            num_requests = 0

            @staticmethod
            def post(url, data, timeout, *args, **kwargs):
                assert url in (url_hub, url_other_hub)

                if wanted_timeout:
                    # Test that the timeout is equal what we put in
                    assertEqual(wanted_timeout, timeout)
                else:
                    # Test that the default timeout is OK
                    assert 5.0 < timeout < 30.0, "Too long or short timeout!"

                assert ("hub.mode", "publish") in data, \
                    "Pair (hub.mode, publish) not in %s" % data
                for url_feed in (podcast.feed_url for podcast in feeds
                                 if podcast.pubsubhubbub == url):
                    assert ("hub.url", url_feed) in data, \
                        "Pair (hub.url, %s) not in %s" % (url_feed, data)
                    MyLittleRequests.num_feeds += 1

                class MyLittleResponse(object):
                    def raise_for_status(self):
                        pass
                MyLittleRequests.num_requests += 1
                return MyLittleResponse()

        Podcast.notify_multiple(MyLittleRequests, feeds)
        self.assertEqual(MyLittleRequests.num_feeds, 3)
        self.assertEqual(MyLittleRequests.num_requests, 1)

        # Test with timeout
        wanted_timeout = 50.0
        Podcast.notify_multiple(MyLittleRequests, feeds, timeout=wanted_timeout)
        self.assertEqual(MyLittleRequests.num_feeds, 6)
        self.assertEqual(MyLittleRequests.num_requests, 2)

        # Test with one feed with another pubsubhubbub
        wanted_timeout = None
        feeds.append(Podcast(
            name="Test4",
            description="Testing another pubsubhubbub",
            website="http://example.com",
            explicit=True,
            feed_url="http://example.com/feed4.rss",
            pubsubhubbub=url_other_hub
        ))
        Podcast.notify_multiple(MyLittleRequests, feeds)
        self.assertEqual(MyLittleRequests.num_feeds, 10)
        self.assertEqual(MyLittleRequests.num_requests, 4)


if __name__ == '__main__':
    unittest.main()
