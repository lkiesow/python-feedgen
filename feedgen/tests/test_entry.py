# -*- coding: utf-8 -*-

"""
Tests for a basic entry

These are test cases for a basic entry.
"""

import unittest
from lxml import etree

from feedgen.person import Person
from feedgen.media import Media
from ..feed import Podcast
import datetime
import pytz
from dateutil.parser import parse as parsedate

class TestBaseEpisode(unittest.TestCase):

    def setUp(self):

        self.itunes_ns = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        self.dublin_ns = 'http://purl.org/dc/elements/1.1/'

        fg = Podcast()
        self.title = 'Some Testfeed'
        self.link = 'http://lernfunk.de'
        self.description = 'A cool tent'
        self.explicit = False

        fg.name(self.title)
        fg.website(self.link)
        fg.description(self.description)
        fg.itunes_explicit(self.explicit)

        fe = fg.add_episode()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The First Episode')
        self.fe = fe

        #Use also the list directly
        fe = fg.Episode()
        fg.episodes.append(fe)
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Second Episode')

        fe = fg.add_episode()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Third Episode')

        self.fg = fg

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
        episode.enclosure(Media(guid, 97423487, "audio/mpeg"))

        item = episode.rss_entry()
        assert item.find("guid").text == guid

    def test_idSetToFalseSoEnclosureNotUsed(self):
        episode = self.fg.Episode()
        episode.title("My first episode")
        episode.enclosure(Media("http://example.com/podcast/episode1.mp3",
                                34328731, "audio/mpeg"))
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

    def test_oneAuthor(self):
        name = "John Doe"
        email = "johndoe@example.org"
        self.fe.authors = [Person(name, email)]
        author_text = self.fe.rss_entry().find("author").text
        assert name in author_text
        assert email in author_text

        # Test that itunes:author is the name
        assert self.fe.rss_entry().find("{%s}author" % self.itunes_ns).text\
            == name
        # Test that dc:creator is not used when rss author does the same job
        assert self.fe.rss_entry().find("{%s}creator" % self.dublin_ns) is None

    def test_oneAuthorWithoutEmail(self):
        name = "John Doe"
        self.fe.authors.append(Person(name))
        entry = self.fe.rss_entry()

        # Test that author is not used, since it requires email
        assert entry.find("author") is None
        # Test that itunes:author is still the name
        assert entry.find("{%s}author" % self.itunes_ns).text == name
        # Test that dc:creator is used in rss author's place (since dc:creator
        # doesn't require email)
        assert entry.find("{%s}creator" % self.dublin_ns).text == name

    def test_oneAuthorWithoutName(self):
        email = "johndoe@example.org"
        self.fe.authors.extend([Person(email=email)])
        entry = self.fe.rss_entry()

        # Test that rss author is the email
        assert entry.find("author").text == email
        # Test that itunes:author is not used, since it requires name
        assert entry.find("{%s}author" % self.itunes_ns) is None
        # Test that dc:creator is not used, since it would duplicate rss author
        assert entry.find("{%s}creator" % self.dublin_ns) is None


    def test_multipleAuthors(self):
        person1 = Person("John Doe", "johndoe@example.org")
        person2 = Person("Mary Sue", "marysue@example.org")

        self.fe.authors = [person1, person2]
        author_elements = \
            self.fe.rss_entry().findall("{%s}creator" % self.dublin_ns)
        author_texts = [e.text for e in author_elements]

        # Test that both authors are included, in the same order they were added
        assert person1.name in author_texts[0]
        assert person1.email in author_texts[0]
        assert person2.name in author_texts[1]
        assert person2.email in author_texts[1]

        # Test that itunes:author includes all authors' name, but not email
        itunes_author = \
            self.fe.rss_entry().find("{%s}author" % self.itunes_ns).text
        assert person1.name in itunes_author
        assert person1.email not in itunes_author
        assert person2.name in itunes_author
        assert person2.email not in itunes_author

        # Test that the regular rss tag is not used, per the RSS recommendations
        assert self.fe.rss_entry().find("author") is None

    def test_authorsInvalidAssignment(self):
        self.assertRaises(TypeError, self.do_authorsInvalidAssignment)

    def do_authorsInvalidAssignment(self):
        self.fe.authors = Person("Oh No", "notan@iterable.no")

    def test_media(self):
        media = Media("http://example.org/episodes/1.mp3", 14536453,
                      "audio/mpeg")
        self.fe.enclosure(media)
        enclosure = self.fe.rss_entry().find("enclosure")

        self.assertEqual(enclosure.get("url"), media.url)
        self.assertEqual(enclosure.get("length"), str(media.size))
        self.assertEqual(enclosure.get("type"), media.type)

        # Ensure duck-typing is checked at assignment time
        self.assertRaises(TypeError, self.fe.enclosure, media.url)
        self.assertRaises(TypeError, self.fe.enclosure,
                          (media.url, media.size, media.type))
