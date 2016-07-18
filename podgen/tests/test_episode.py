# -*- coding: utf-8 -*-
"""
    podgen.tests.test_episode
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Test the Episode class.

    :copyright: 2016, Thorben Dahl <thorben@sjostrom.no>
    :license: FreeBSD and LGPL, see license.* for more details.
"""

import unittest
import warnings

from lxml import etree

from podgen import Person, Media, Podcast, htmlencode, Episode, \
    NotSupportedByItunesWarning
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

        fg.name = self.title
        fg.website = self.link
        fg.description = self.description
        fg.explicit = self.explicit

        fe = fg.add_episode()
        fe.id = 'http://lernfunk.de/media/654321/1'
        fe.title = 'The First Episode'
        self.fe = fe

        #Use also the list directly
        fe = Episode()
        fg.episodes.append(fe)
        fe.id = 'http://lernfunk.de/media/654321/1'
        fe.title = 'The Second Episode'

        fe = fg.add_episode()
        fe.id = 'http://lernfunk.de/media/654321/1'
        fe.title = 'The Third Episode'

        self.fg = fg

        warnings.simplefilter("always")
        def noop(*args, **kwargs):
            pass
        warnings.showwarning = noop

    def test_constructor(self):
        title = "A constructed episode"
        subtitle = "We're using the constructor!"
        summary = "In this week's episode, we try using the constructor to " \
                  "create a new Episode object."
        long_summary = "In this week's episode, we try to use the constructor " \
                       "to create a new Episode object. Additionally, we'll " \
                       "check whether it actually worked or not. Hold your " \
                       "fingers crossed!"
        media = Media("http://example.com/episodes/1.mp3", 1425345346,
                      "audio/mpeg",
                      datetime.timedelta(hours=1, minutes=2, seconds=22))
        publication_date = datetime.datetime(2016, 6, 7, 13, 37, 0,
                                             tzinfo=pytz.utc)
        link = "http://example.com/blog/?i=1"
        authors = [Person("John Doe", "johndoe@example.com")]
        image = "http://example.com/static/1.png"
        explicit = True
        is_closed_captioned = False
        position = 3
        withhold_from_itunes = True

        ep = Episode(
            title=title,
            subtitle=subtitle,
            summary=summary,
            long_summary=long_summary,
            media=media,
            publication_date=publication_date,
            link=link,
            authors=authors,
            image=image,
            explicit=explicit,
            is_closed_captioned=is_closed_captioned,
            position=position,
            withhold_from_itunes=withhold_from_itunes,
        )

        # Time to check if this works
        self.assertEqual(ep.title, title)
        self.assertEqual(ep.subtitle, subtitle)
        self.assertEqual(ep.summary, summary)
        self.assertEqual(ep.long_summary, long_summary)
        self.assertEqual(ep.media, media)
        self.assertEqual(ep.publication_date, publication_date)
        self.assertEqual(ep.link, link)
        self.assertEqual(ep.authors, authors)
        self.assertEqual(ep.image, image)
        self.assertEqual(ep.explicit, explicit)
        self.assertEqual(ep.is_closed_captioned, is_closed_captioned)
        self.assertEqual(ep.position, position)
        self.assertEqual(ep.withhold_from_itunes, withhold_from_itunes)

    def test_constructorUnknownKeyword(self):
        self.assertRaises(TypeError, Episode, tittel="What is tittel")
        self.assertRaises(TypeError, Episode, "This is not a keyword")

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
        fe.id = 'http://lernfunk.de/media/654321/1'
        fe.title = 'The Third BaseEpisode'
        assert len(fg.episodes) == 1
        fg.episodes.pop(0)
        assert len(fg.episodes) == 0

    def test_removeEntryByEntry(self):
        fg = Podcast()
        self.feedId = 'http://example.com'
        self.title = 'Some Testfeed'

        fe = fg.add_episode()
        fe.id = 'http://lernfunk.de/media/654321/1'
        fe.title = 'The Third BaseEpisode'

        assert len(fg.episodes) == 1
        fg.episodes.remove(fe)
        assert len(fg.episodes) == 0

    def test_idIsSet(self):
        guid = "http://example.com/podcast/episode1"
        episode = Episode()
        episode.title = "My first episode"
        episode.id = guid
        item = episode.rss_entry()

        assert item.find("guid").text == guid

    def test_idNotSetButEnclosureIsUsed(self):
        guid = "http://example.com/podcast/episode1.mp3"
        episode = Episode()
        episode.title = "My first episode"
        episode.media = Media(guid, 97423487, "audio/mpeg")

        item = episode.rss_entry()
        assert item.find("guid").text == guid

    def test_idSetToFalseSoEnclosureNotUsed(self):
        episode = Episode()
        episode.title = "My first episode"
        episode.media = Media("http://example.com/podcast/episode1.mp3",
                            34328731, "audio/mpeg")
        episode.id = False

        item = episode.rss_entry()
        assert item.find("guid") is None

    def test_feedPubDateUsesNewestEpisode(self):
        self.fg.episodes[0].publication_date = \
            datetime.datetime(2015, 1, 1, 15, 0, tzinfo=pytz.utc)
        self.fg.episodes[1].publication_date = \
            datetime.datetime(2016, 1, 3, 12, 22, tzinfo=pytz.utc)
        self.fg.episodes[2].publication_date = \
            datetime.datetime(2014, 3, 2, 13, 11, tzinfo=pytz.utc)
        rss = self.fg._create_rss()
        pubDate = rss.find("channel").find("pubDate")
        assert pubDate is not None
        parsedPubDate = parsedate(pubDate.text)
        assert parsedPubDate == self.fg.episodes[1].publication_date

    def test_feedPubDateNotOverriddenByEpisode(self):
        self.fg.episodes[0].publication_date = \
            datetime.datetime(2015, 1, 1, 15, 0, tzinfo=pytz.utc)
        pubDate = self.fg._create_rss().find("channel").find("pubDate")
        # Now it uses the episode's published date
        assert pubDate is not None
        assert parsedate(pubDate.text) == self.fg.episodes[0].publication_date

        new_date = datetime.datetime(2016, 1, 2, 3, 4, tzinfo=pytz.utc)
        self.fg.publication_date = new_date
        pubDate = self.fg._create_rss().find("channel").find("pubDate")
        # Now it uses the custom-set date
        assert pubDate is not None
        assert parsedate(pubDate.text) == new_date

    def test_feedPubDateDisabled(self):
        self.fg.episodes[0].publication_date = \
            datetime.datetime(2015, 1, 1, 15, 0, tzinfo=pytz.utc)
        self.fg.publication_date = False
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
        self.fe.media = media
        enclosure = self.fe.rss_entry().find("enclosure")

        self.assertEqual(enclosure.get("url"), media.url)
        self.assertEqual(enclosure.get("length"), str(media.size))
        self.assertEqual(enclosure.get("type"), media.type)

        # Ensure duck-typing is checked at assignment time
        self.assertRaises(TypeError, setattr, self.fe, "media", media.url)
        self.assertRaises(TypeError, setattr, self.fe, "media",
                          (media.url, media.size, media.type))

    def test_withholdFromItunesOffByDefault(self):
        assert not self.fe.withhold_from_itunes

    def test_withholdFromItunes(self):
        self.fe.withhold_from_itunes = True
        itunes_block = self.fe.rss_entry().find("{%s}block" % self.itunes_ns)
        assert itunes_block is not None
        self.assertEqual(itunes_block.text.lower(), "yes")

        self.fe.withhold_from_itunes = False
        itunes_block = self.fe.rss_entry().find("{%s}block" % self.itunes_ns)
        assert itunes_block is None

    def test_summaries(self):
        content_encoded = "{%s}encoded" % \
                          "http://purl.org/rss/1.0/modules/content/"
        # Test that none are in use by default (no summary is set)
        d = self.fe.rss_entry().find("description")
        assert d is None
        ce = self.fe.rss_entry().find(content_encoded)
        assert ce is None

        # Test that description is filled when one of the summaries is set
        self.fe.summary = "A short summary"
        d = self.fe.rss_entry().find("description")
        assert d is not None
        assert "A short summary" == d.text
        ce = self.fe.rss_entry().find(content_encoded)
        assert ce is None

        self.fe.summary = False
        self.fe.long_summary = "A long summary with more words"
        d = self.fe.rss_entry().find("description")
        assert d is not None
        assert "A long summary with more words" == d.text
        ce = self.fe.rss_entry().find(content_encoded)
        assert ce is None

        # Test that description and content:encoded are used when both are set
        self.fe.summary = "A short summary"
        self.fe.long_summary = "A long summary with more words"
        d = self.fe.rss_entry().find("description")
        assert d is not None
        assert "A short summary" == d.text
        ce = self.fe.rss_entry().find(content_encoded)
        assert ce is not None
        assert "A long summary with more words" == ce.text

    def test_summariesHtml(self):
        self.fe.summary = "A <b>cool</b> summary"
        d = self.fe.rss_entry().find("description")
        assert d is not None
        assert "A <b>cool</b> summary" == d.text

        self.fe.summary = htmlencode("A <b>cool</b> summary")
        d = self.fe.rss_entry().find("description")
        assert d is not None
        assert "A &lt;b&gt;cool&lt;/b&gt; summary" == d.text

    def test_position(self):
        # Test that position is set (testing Podcast and Episode)
        self.fg.apply_episode_order()
        self.assertEqual(self.fg.episodes[0].position, 1)
        self.assertEqual(self.fg.episodes[1].position, 2)
        self.assertEqual(self.fg.episodes[2].position, 3)

        # Test that position is also output as part of RSS (testing Episode)
        itunes_order = self.fe.rss_entry().find("{%s}order" % self.itunes_ns)
        assert itunes_order is not None
        self.assertEqual(itunes_order.text, str(self.fe.position))

        # Test that clearing works (testing Podcast and Episode)
        self.fg.clear_episode_order()
        assert self.fg.episodes[0].position is None
        assert self.fg.episodes[1].position is None
        assert self.fg.episodes[2].position is None

        # No longer itunes:order element (testing Episode)
        itunes_order = self.fe.rss_entry().find("{%s}order" % self.itunes_ns)
        assert itunes_order is None

    def test_mandatoryAttributes(self):
        ep = Episode()
        self.assertRaises((RuntimeError, ValueError), ep.rss_entry)

        ep.title = "A title"
        ep.rss_entry()

        ep.title = ""
        self.assertRaises((RuntimeError, ValueError), ep.rss_entry)

        ep.title = None
        self.assertRaises((RuntimeError, ValueError), ep.rss_entry)

        ep.summary = "A summary"
        ep.rss_entry()

        ep.summary = ""
        self.assertRaises((RuntimeError, ValueError), ep.rss_entry)

        ep.summary = None
        self.assertRaises((RuntimeError, ValueError), ep.rss_entry)

    def test_explicit(self):
        # Don't appear if None (use podcast's explicit value)
        assert self.fe.explicit is None
        assert self.fe.rss_entry().find("{%s}explicit" % self.itunes_ns) is None

        # Appear and say it's explicit if True
        self.fe.explicit = True
        itunes_explicit = self.fe.rss_entry()\
            .find("{%s}explicit" % self.itunes_ns)
        assert itunes_explicit is not None
        assert itunes_explicit.text.lower() in ("yes", "explicit", "true")

        # Appear and say it's clean if False
        self.fe.explicit = False
        itunes_explicit = self.fe.rss_entry()\
            .find("{%s}explicit" % self.itunes_ns)
        assert itunes_explicit is not None
        assert itunes_explicit.text.lower() in ("no", "clean", "false")

    def test_image(self):
        # Test that the attribute works
        assert self.fe.image is None

        image = "https://static.example.org/img/hello.png"
        self.fe.image = image
        self.assertEqual(self.fe.image, image)

        # Test that it appears in XML
        itunes_image = self.fe.rss_entry().find("{%s}image" % self.itunes_ns)
        assert itunes_image is not None

        # Test that its contents is correct
        self.assertEqual(itunes_image.get("href"), image)
        assert itunes_image.text is None

    def test_imageWarningNoExt(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(len(w), 0)

            # Set image to a URL without proper file extension
            no_ext = "http://static.example.com/images/logo"
            self.fe.image = no_ext
            # Did we get a warning?
            self.assertEqual(1, len(w))
            assert issubclass(w.pop().category, NotSupportedByItunesWarning)
            # Was the image set?
            self.assertEqual(no_ext, self.fe.image)

    def test_imageWarningBadExt(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Set image to a URL with an unsupported file extension
            bad_ext = "http://static.example.com/images/logo.gif"
            self.fe.image = bad_ext
            # Did we get a warning?
            self.assertEqual(1, len(w))
            # Was it of the correct type?
            assert issubclass(w.pop().category, NotSupportedByItunesWarning)
            # Was the image still set?
            self.assertEqual(bad_ext, self.fe.image)

    def test_imageNoWarningWithGoodExt(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Set image to a URL with a supported file extension
            extensions = ["jpg", "png", "jpeg"]
            for extension in extensions:
                good_ext = "http://static.example.com/images/logo." + extension
                self.fe.image = good_ext
                # Did we get no warning?
                self.assertEqual(0, len(w), "Extension %s raised warnings (%s)"
                                 % (extension, w))
                # Was the image set?
                self.assertEqual(good_ext, self.fe.image)

    def test_isClosedCaptioned(self):
        def get_element():
            return self.fe.rss_entry()\
                .find("{%s}isClosedCaptioned" % self.itunes_ns)

        # Starts out as False or None
        assert self.fe.is_closed_captioned is None or \
            self.fe.is_closed_captioned is False

        # Not used when set to False
        self.fe.is_closed_captioned = False
        self.assertEqual(self.fe.is_closed_captioned, False)
        assert get_element() is None

        # Not used when set to None
        self.fe.is_closed_captioned = None
        assert self.fe.is_closed_captioned is None
        assert get_element() is None

        # Used and says "yes" when set to True
        self.fe.is_closed_captioned = True
        self.assertEqual(self.fe.is_closed_captioned, True)
        assert get_element() is not None
        self.assertEqual(get_element().text.lower(), "yes")

    def test_link(self):
        def get_element():
            return self.fe.rss_entry().find("link")

        # Starts out as None or empty
        assert self.fe.link is None or self.fe.link == ""

        # Not used when set to None
        self.fe.link = None
        assert self.fe.link is None
        assert get_element() is None

        # Not used when set to empty
        self.fe.link = ""
        assert self.fe.link == ""
        assert get_element() is None

        # Used when set to something
        link = "http://example.com/episode1.html"
        self.fe.link = link
        self.assertEqual(self.fe.link, link)
        assert get_element() is not None
        self.assertEqual(get_element().text, link)

    def test_subtitle(self):
        def get_element():
            return self.fe.rss_entry().find("{%s}subtitle" % self.itunes_ns)

        # Starts out as None or empty
        assert self.fe.subtitle is None or self.fe.subtitle == ""

        # Not used when set to None
        self.fe.subtitle = None
        assert self.fe.subtitle is None
        assert get_element() is None

        # Not used when set to empty
        self.fe.subtitle = ""
        self.assertEqual(self.fe.subtitle, "")
        assert get_element() is None

        # Used when set to something
        subtitle = "This is a subtitle"
        self.fe.subtitle = subtitle
        self.assertEqual(self.fe.subtitle, subtitle)
        element = get_element()
        assert element is not None
        self.assertEqual(element.text, subtitle)

    def test_title(self):
        ep = Episode()

        def get_element():
            return ep.rss_entry().find("title")
        # Starts out as None or empty.
        assert ep.title is None or ep.title == ""

        # We test that you cannot create RSS when it's empty or blank in
        # another method.

        # Test that it is set correctly
        ep.title = None
        assert ep.title is None

        ep.title = ""
        self.assertEqual(ep.title, "")

        # Test that the title is used correctly
        title = "My Fine Title"
        ep.title = title
        self.assertEqual(ep.title, title)

        element = get_element()
        assert element is not None
        self.assertEqual(element.text, title)
