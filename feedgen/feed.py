# -*- coding: utf-8 -*-
"""
    feedgen.feed
    ~~~~~~~~~~~~

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.

"""

from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from feedgen.item import BaseEpisode
from feedgen.util import ensure_format, formatRFC2822, listToHumanreadableStr
from feedgen.person import Person
import feedgen.version
import sys
from feedgen.compat import string_types
import collections
import inspect


_feedgen_version = feedgen.version.version_str


class Podcast(object):
    """Class representing one podcast feed.
    """


    def __init__(self):
        self.__episodes = []
        """The list used by self.episodes."""
        self.__episode_class = BaseEpisode
        """The internal value used by self.Episode."""

        ## RSS
        # http://www.rssboard.org/rss-specification
        # Mandatory:
        self.__rss_title       = None
        self.__rss_link        = None
        self.__rss_description = None

        # Optional:
        self.__rss_cloud          = None
        self.__rss_copyright      = None
        self.__rss_docs           = 'http://www.rssboard.org/rss-specification'
        self.__rss_generator      = self._feedgen_generator_str
        self.__rss_language       = None
        self.__rss_lastBuildDate  = None
        self.__rss_author = None
        self.__rss_pubDate        = None
        self.__rss_skipHours      = None
        self.__rss_skipDays       = None
        self.__rss_webMaster      = None

        self.__self_link = None

        ## ITunes tags
        # http://www.apple.com/itunes/podcasts/specs.html#rss
        self.__itunes_block = None
        self.__itunes_category = None
        self.__itunes_image = None
        self.__itunes_explicit = None
        self.__itunes_complete = None
        self.__itunes_new_feed_url = None
        self.__itunes_owner = None
        self.__itunes_subtitle = None

    @property
    def episodes(self):
        """List of episodes that are part of this podcast.

        This property is read-only, in the sense that you cannot assign a new list to it.
        You are, however, able to add, get and remove individual episodes from the (existing) list.

        See :py:meth:`.add_episode` for an easy way to create new episodes and assign them to this podcast
        in one call.
        """
        return self.__episodes

    @property
    def Episode(self):
        """Class used to represent episodes.

        This is actually a property (variable) which points to the correct
        class. It is used by :py:meth:`.add_episode` when creating new episode
        objects, and you should use it too when adding episodes.

        By default, this property points to :py:class:`BaseEpisode`.

        When assigning a new class to Episode, you must make sure the new value
        (1) is a class and not an instance, and (2) is a subclass of BaseEpisode
        (or is BaseEpisode itself).

        This property exists so you can change which class episodes should have, without needing to change the code
        that creates those episodes. Thus, changing this property changes what class is used by self.add_episode().
        An example would be if you created a subclass of Podcast together with a
        subclass of Episode, and wanted users of your new Podcast subclass to be using your new Episode subclass
        automatically. All you need to do, is to change the initial value of Episode in your Podcast subclass.
        Another example is if you want to use another class for episodes, while
        still enjoying the benefits of using :py:meth:`.add_episode`.
        You as a users, on the other hand, won't have to change your code when changing between different
        subclasses of Podcast that expect different subclasses of Episode.

        It is still possible for you to hardcode what Episode subclass you want to use, either by calling its
        constructor without using this property, or by overriding its value.

        Example of use::

            >>> # Create new podcast
            >>> from feedgen.feed import Podcast
            >>> p = Podcast()

            >>> # Here's how you would create a new episode object, the OK way
            >>> episode1 = p.Episode()
            >>> p.episodes.append(episode1)
            >>> episode1.title("My awesome episode")

            >>> # Best way to create new episode object (it is added to the podcast automatically)
            >>> episode2 = p.add_episode()
            >>> episode2.title("My even more awesome episode")

            >>> # If you want to use another class for episodes, do it like this
            >>> from mymodule import AlternateEpisode
            >>> p.Episode = AlternateEpisode
            >>> episode3 = p.add_episode()  # It is also okay to use p.episodes
            >>> episode3.title("This is an instance of AlternateEpisode!")

            >>> # !!! DON'T DO THE FOLLOWING, unless you want to hard code what class is used !!!
            >>> episode3 = AlternateEpisode()
            >>> p.episodes.append(episode3)  # or p.add_episode(episode3)
            >>> episode3.title("My awful episode :(")
        """
        return self.__episode_class

    @Episode.setter
    def Episode(self, value):
        if not inspect.isclass(value):
            raise ValueError("New Episode must NOT be an _instance_ of the desired class, but rather the class "
                             "itself. You can generally achieve this by removing the parenthesis from the "
                             "constructor call. For example, use Episode, not Episode().")
        elif issubclass(value, BaseEpisode):
            self.__episode_class = value
        else:
            raise ValueError("New Episode must be Episode or a descendant of it (so the API still works).")

    def add_episode(self, new_episode=None):
        """Shorthand method which adds a new episode to the feed, creating an
        object if it's not provided, and returns it. This
        is the easiest way to add episodes to a podcast.

        :param new_episode: Episode object to add. A new instance of
            self.Episode is used if new_episode is omitted.
        :returns: Episode object created or passed to this function.

        Example::

            ...
            >>> entry = feedgen.add_episode()
            >>> entry.title('First feed entry')
            'First feed entry'
            >>> # You may also provide an episode object yourself:
            >>> another_entry = feedgen.add_episode(feedgen.Episode())
            >>> another_entry.title('My second feed entry')
            'My second feed entry'

        For the curious, this is a shorthand method which basically reads like::

            if new_episode is None:
                new_episode = self.Episode()
            self.episodes.append(new_episode)
            return new_episode

        """
        if new_episode is None:
            new_episode = self.Episode()
        self.episodes.append(new_episode)
        return new_episode

    def _create_rss(self):
        """Create an RSS feed XML structure containing all previously set fields.

        :returns: The root element (ie. the rss element) of the feed.
        :rtype: lxml.etree.Element
        """

        nsmap = {
            'atom':  'http://www.w3.org/2005/Atom',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }

        ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'

        feed = etree.Element('rss', version='2.0', nsmap=nsmap )
        channel = etree.SubElement(feed, 'channel')
        if not ( self.__rss_title and self.__rss_link and self.__rss_description ):
            missing = ', '.join(([] if self.__rss_title else ['title']) + \
                    ([] if self.__rss_link else ['link']) + \
                    ([] if self.__rss_description else ['description']))
            raise ValueError('Required fields not set (%s)' % missing)
        title = etree.SubElement(channel, 'title')
        title.text = self.__rss_title
        link = etree.SubElement(channel, 'link')
        link.text = self.__rss_link
        desc = etree.SubElement(channel, 'description')
        desc.text = self.__rss_description

        if self.__rss_cloud:
            cloud = etree.SubElement(channel, 'cloud')
            cloud.attrib['domain'] = self.__rss_cloud.get('domain')
            cloud.attrib['port'] = str(self.__rss_cloud.get('port'))
            cloud.attrib['path'] = self.__rss_cloud.get('path')
            cloud.attrib['registerProcedure'] = self.__rss_cloud.get(
                    'registerProcedure')
            cloud.attrib['protocol'] = self.__rss_cloud.get('protocol')
        if self.__rss_copyright:
            copyright = etree.SubElement(channel, 'copyright')
            copyright.text = self.__rss_copyright
        if self.__rss_docs:
            docs = etree.SubElement(channel, 'docs')
            docs.text = self.__rss_docs
        if self.__rss_generator:
            generator = etree.SubElement(channel, 'generator')
            generator.text = self.__rss_generator
        if self.__rss_language:
            language = etree.SubElement(channel, 'language')
            language.text = self.__rss_language

        if self.__rss_lastBuildDate is None:
            lastBuildDateDate = datetime.now(dateutil.tz.tzutc())
        else:
            lastBuildDateDate = self.__rss_lastBuildDate
        if lastBuildDateDate:
            lastBuildDate = etree.SubElement(channel, 'lastBuildDate')
            lastBuildDate.text = formatRFC2822(lastBuildDateDate)

        if self.__rss_author:
            authors_with_name = [a.name for a in self.__rss_author if a.name]
            if authors_with_name:
                # We have something to display as itunes:author, combine all
                # names
                itunes_author = \
                    etree.SubElement(channel, '{%s}author' % ITUNES_NS)
                itunes_author.text = listToHumanreadableStr(authors_with_name)
            if len(self.__rss_author) > 1 or not self.__rss_author[0].email:
                # Use dc:creator, since it supports multiple authors (and
                # author without email)
                for a in self.__rss_author or []:
                    author = etree.SubElement(channel,
                                              '{%s}creator' % nsmap['dc'])
                    if a.name and a.email:
                        author.text = "%s <%s>" % (a.name, a.email)
                    elif a.name:
                        author.text = a.name
                    else:
                        author.text = a.email
            else:
                # Only one author and with email, so use rss managingEditor
                author = etree.SubElement(channel, 'managingEditor')
                author.text = str(self.__rss_author[0])

        if self.__rss_pubDate is None:
            episode_dates = [e.published() for e in self.episodes if e.published() is not None]
            if episode_dates:
                actual_pubDate = max(episode_dates)
            else:
                actual_pubDate = None
        else:
            actual_pubDate = self.__rss_pubDate
        if actual_pubDate:
            pubDate = etree.SubElement(channel, 'pubDate')
            pubDate.text = formatRFC2822(actual_pubDate)

        if self.__rss_skipHours:
            skipHours = etree.SubElement(channel, 'skipHours')
            for h in self.__rss_skipHours:
                hour = etree.SubElement(skipHours, 'hour')
                hour.text = str(h)
        if self.__rss_skipDays:
            skipDays = etree.SubElement(channel, 'skipDays')
            for d in self.__rss_skipDays:
                day = etree.SubElement(skipDays, 'day')
                day.text = d
        if self.__rss_webMaster:
            if not self.__rss_webMaster.email:
                raise RuntimeError("webMaster must have an email. Did you "
                                   "set email to None after assigning that "
                                   "Person to webMaster?")
            webMaster = etree.SubElement(channel, 'webMaster')
            webMaster.text = str(self.__rss_webMaster)

        if not self.__itunes_block is None:
            block = etree.SubElement(channel, '{%s}block' % ITUNES_NS)
            block.text = 'yes' if self.__itunes_block else 'no'

        if self.__itunes_category:
            category = etree.SubElement(channel, '{%s}category' % ITUNES_NS)
            category.attrib['text'] = self.__itunes_category['cat']
            if self.__itunes_category.get('sub'):
                subcategory = etree.SubElement(category, '{%s}category' % ITUNES_NS)
                subcategory.attrib['text'] = self.__itunes_category['sub']

        if self.__itunes_image:
            image = etree.SubElement(channel, '{%s}image' % ITUNES_NS)
            image.attrib['href'] = self.__itunes_image

        if self.__itunes_explicit in ('yes', 'no', 'clean'):
            explicit = etree.SubElement(channel, '{%s}explicit' % ITUNES_NS)
            explicit.text = self.__itunes_explicit

        if self.__itunes_complete in ('yes', 'no'):
            complete = etree.SubElement(channel, '{%s}complete' % ITUNES_NS)
            complete.text = self.__itunes_complete

        if self.__itunes_new_feed_url:
            new_feed_url = etree.SubElement(channel, '{%s}new-feed-url' % ITUNES_NS)
            new_feed_url.text = self.__itunes_new_feed_url

        if self.__itunes_owner:
            owner = etree.SubElement(channel, '{%s}owner' % ITUNES_NS)
            owner_name = etree.SubElement(owner, '{%s}name' % ITUNES_NS)
            owner_name.text = self.__itunes_owner.name
            owner_email = etree.SubElement(owner, '{%s}email' % ITUNES_NS)
            owner_email.text = self.__itunes_owner.email

        if self.__itunes_subtitle:
            subtitle = etree.SubElement(channel, '{%s}subtitle' % ITUNES_NS)
            subtitle.text = self.__itunes_subtitle

        if self.__self_link:
            link_to_self = etree.SubElement(channel, '{%s}link' % nsmap['atom'])
            link_to_self.attrib['href'] = self.__self_link
            link_to_self.attrib['rel'] = 'self'
            link_to_self.attrib['type'] = 'application/rss+xml'

        for entry in self.episodes:
            item = entry.rss_entry()
            channel.append(item)

        return feed

    def __str__(self):
        """Print the podcast in RSS format, using the default options.

        This method just calls :py:meth:`.rss_str` without arguments.
        """
        return self.rss_str()

    def rss_str(self, minimize=False, encoding='UTF-8',
                xml_declaration=True):
        """Generates an RSS feed and returns the feed XML as string.

        :param minimize: Set to True to disable splitting the feed into multiple
            lines and adding properly indentation, saving bytes at the cost of
            readability.
        :type minimize: bool
        :param encoding: Encoding used in the XML file (default: UTF-8).
        :type encoding: str
        :param xml_declaration: If an XML declaration should be added to the
            output (Default: enabled).
        :type xml_declaration: bool
        :returns: String representation of the RSS feed.
        """
        feed = self._create_rss()
        return etree.tostring(feed, pretty_print=not minimize, encoding=encoding,
                              xml_declaration=xml_declaration).decode(encoding)


    def rss_file(self, filename, minimize=False,
                 encoding='UTF-8', xml_declaration=True):
        """Generates an RSS feed and write the resulting XML to a file.

        :param filename: Name of file to write, or a file-like object, or a URL.
        :type filename: str or fd
        :param minimize: Set to True to disable splitting the feed into multiple
            lines and adding properly indentation, saving bytes at the cost of
            readability.
        :type minimize: bool
        :param encoding: Encoding used in the  XML file (default: UTF-8).
        :type encoding: str
        :param xml_declaration: If an XML declaration should be added to the
            output (Default: enabled).
        :type xml_declaration: bool
        """
        feed = self._create_rss()
        doc = etree.ElementTree(feed)
        doc.write(filename, pretty_print=not minimize, encoding=encoding,
                  xml_declaration=xml_declaration)


    def name(self, name=None):
        """Get or set the name of the podcast. It should be a human
        readable title. Often the same as the title of the
        associated website. This is mandatory for RSS and must
        not be blank.

        :param name: The new name of the podcast.
        :type name: str
        :returns: The podcast's name.
        """
        if not name is None:
            self.__rss_title = name
        return self.__rss_title


    def updated(self, updated=None):
        """Set or get the updated value which indicates the last time the feed
        was modified in a significant way.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        This will set rss:lastBuildDate.

        Default value
            If not set, updated has as value the current date and time.

        Set this to False to have no updated value in the feed.

        :param updated: The modification date.
        :type updated: str or datetime.datetime
        :returns: Modification date as datetime.datetime
        """
        if not updated is None:
            if updated is False:
                self.__rss_lastBuildDate = False
            else:
                if isinstance(updated, string_types):
                    updated = dateutil.parser.parse(updated)
                if not isinstance(updated, datetime):
                    raise ValueError('Invalid datetime format')
                if updated.tzinfo is None:
                    raise ValueError('Datetime object has no timezone info')
                self.__rss_lastBuildDate = updated

        return self.__rss_lastBuildDate


    def website(self, href=None):
        """Get or set this podcast's website.

        This corresponds to the RSS link element.

        :param href: URI of this podcast's website.

        Example::

            >>> feedgen.website( href='http://example.com/')

        """
        if not href is None:
            self.__rss_link = href
        return self.__rss_link


    def cloud(self, domain=None, port=None, path=None, registerProcedure=None,
            protocol=None):
        """Set or get the cloud data of the feed. It is an RSS only attribute. It
        specifies a web service that supports the rssCloud interface which can be
        implemented in HTTP-POST, XML-RPC or SOAP 1.1.

        :param domain: The domain where the webservice can be found.
        :param port: The port the webservice listens to.
        :param path: The path of the webservice.
        :param registerProcedure: The procedure to call.
        :param protocol: Can be either "HTTP-POST", "xml-rpc" or "soap".
        :returns: Dictionary containing the cloud data.
        """
        if not domain is None:
            if not (domain and (port != False) and path and registerProcedure
                    and protocol):
                raise ValueError("All parameters of cloud must be present and"
                                 " not empty.")
            self.__rss_cloud = {'domain':domain, 'port':port, 'path':path,
                    'registerProcedure':registerProcedure, 'protocol':protocol}
        return self.__rss_cloud


    def generator(self, generator=None, version=None, uri=None,
                  exclude_feedgen=False):
        """Get or the generator of the feed which identifies the software used to
        generate the feed, for debugging and other purposes.

        :param generator: Software used to create the feed.
        :param version: (Optional) Version of the software, as a tuple.
        :param uri: (Optional) URI the software can be found.
        :param exclude_feedgen: (Optional) Set to True to disable the mentioning
            of the python-feedgen library.
        """
        if not generator is None:
            self.__rss_generator = self._program_name_to_str(generator, version, uri) + \
                                   (" (using %s)" % self._feedgen_generator_str
                                    if not exclude_feedgen else "")
        return self.__rss_generator

    def _program_name_to_str(self, generator=None, version=None, uri=None):
        return generator + \
                ((" v" + ".".join([str(i) for i in version])) if version is not None else "") + \
                ((" " + uri) if uri else "")

    @property
    def _feedgen_generator_str(self):
        return self._program_name_to_str(
                                       feedgen.version.name,
                                       feedgen.version.version_full,
                                       feedgen.version.website
                                   )

    def copyright(self, copyright=None):
        """Get or set the copyright notice for content in this podcast.

        This should be human-readable. For example, "Copyright 2016 Example
        Radio".

        Note that even if you leave out the copyright notice, your content is
        still protected by copyright (unless anything else is indicated), since
        you do not need a copyright statement for something to be protected by
        copyright. If you intend to put the podcast in public domain or license
        it under a Creative Commons license, you should say so in the copyright
        notice.

        :param copyright: The copyright notice.
        :type copyright: str
        :returns: The copyright notice.
        """

        if not copyright is None:
            self.__rss_copyright = copyright
        return self.__rss_copyright


    def description(self, description=None):
        """Set and get the description of the feed,
        which is a phrase or sentence describing the channel. It is mandatory for
        RSS feeds, and is shown under the podcast's name on the iTunes store
        page.

        :param description: Description of the podcast.
        :returns: Description of the podcast.

        """
        if not description is None:
            self.__rss_description = description
        return self.__rss_description


    def language(self, language=None):
        """Get or set the language of the podcast.

        This allows aggregators to group all Italian
        language podcasts, for example, on a single page.

        :param language: The language of the podcast. It must be a two-letter
            code, as found in ISO639-1, with the
            possibility of specifying subcodes (eg. en-US for American English).
            See http://www.rssboard.org/rss-language-codes and
            http://www.loc.gov/standards/iso639-2/php/code_list.php
        :returns: Language of the feed.
        """
        if not language is None:
            self.__rss_language = language
        return self.__rss_language


    def author(self, *author, replace=False):
        """Append or get which person(s) or entity/entities is/are responsible
        for the podcast's editorial content.

        When called multiple times, the authors are appended to the list, unless
        you set replace to ``True``.

        The names supplied are shown on iTunes under the podcast's title.

        One or more :class:`~feedgen.person.Person` objects can be passed to
        this method.

        .. note::

            Remember to unpack any lists you use, since lists are not allowed as
            parameters.

        Example::

            >>> my_authors = [Person("John Doe"), Person("Mary Sue")]
            >>> p.author(*my_authors)
            >>> # Or don't use a list to begin with
            >>> p.author(Person("John Doe"), Person("Mary Sue"), replace=True)

        :param author: One or multiple persons or entities who are
            responsible for the editorial content.
        :type author: feedgen.person.Person
        :param replace: Set to ``True`` to start the list of authors from
            scratch again, thus replacing any authors already on the list.
        :type replace: bool
        :returns: List of :class:`~feedgen.person.Person` responsible for
            editorial content.
        """
        # TODO: Rename author to authors
        if not author is None:
            # Check that the authors quack like ducks
            for a in author:
                if not (hasattr(a, "name") and hasattr(a, "email")):
                    raise TypeError("Author parameter %s does not have the "
                                    "attributes name and/or email. You "
                                    "didn't forget to unpack a list?" % a)

            if replace or self.__rss_author is None:
                self.__rss_author = []
            self.__rss_author.extend(author)
        return self.__rss_author


    def published(self, pubDate=None):
        """Set or get the publication date for the content in the channel. For
        example, the New York Times publishes on a daily basis, the publication
        date flips once every 24 hours. That's when the pubDate of the channel
        changes.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        Default value
            If not set, published will use the value of the episode with the
            latest publication date (which may be in the future). If there
            are no episodes, the publication date is omitted from the feed.

        If you want to omit the publication date from the feed, set pubDate
        to False.

        :param pubDate: The publication date.
        :returns: Publication date as datetime.datetime
        """
        if not pubDate is None:
            if isinstance(pubDate, string_types):
                pubDate = dateutil.parser.parse(pubDate)
            if pubDate is not False and not isinstance(pubDate, datetime):
                raise ValueError('Invalid datetime format')
            elif pubDate is not False and pubDate.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__rss_pubDate = pubDate

        return self.__rss_pubDate


    def skipHours(self, hours=None, replace=False):
        """Set or get which hours feed readers don't need to refresh this feed.

        This method can be called with an hour or a list of hours. The hours are
        represented as integer values from 0 to 23. When called multiple times,
        the new hours are added to the list of existing hours, unless replace
        is True.

        For example, to skip hours between 18 and 7::

            >>> from feedgen.feed import Podcast
            >>> p = Podcast()
            >>> p.skipHours(range(18, 24))
            {18, 19, 20, 21, 22, 23}
            >>> p.skipHours(range(8))
            {0, 1, 2, 3, 4, 5, 6, 7, 18, 19, 20, 21, 22, 23}

        :param hours:   List of hours the feedreaders should not check the feed.
        :type hours: list or set or int
        :param replace: Add or replace old data.
        :returns:       Set of hours the feedreaders should not check the feed.
        """
        if not hours is None:
            if not (isinstance(hours, list) or isinstance(hours, set)):
                hours = [hours]
            for h in hours:
                if not h in range(24):
                    raise ValueError('Invalid hour %s' % h)
            if replace or not self.__rss_skipHours:
                self.__rss_skipHours = set()
            self.__rss_skipHours |= set(hours)
        return self.__rss_skipHours


    def skipDays(self, days=None, replace=False):
        """Set or get the value of skipDays, a hint for aggregators telling them
        which days they can skip.

        This method can be called with a day name or a list of day names. The days are
        represented as strings from 'Monday' to 'Sunday'.

        :param days:   List of days the feedreaders should not check the feed.
        :type days: list or set or str
        :param replace: Add or replace old data.
        :returns:       List of days the feedreaders should not check the feed.
        """
        if not days is None:
            if not (isinstance(days, list) or isinstance(days, set)):
                days = [days]
            for d in days:
                if not d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                        'Friday', 'Saturday', 'Sunday']:
                    raise ValueError('Invalid day %s' % d)
            if replace or not self.__rss_skipDays:
                self.__rss_skipDays = set()
            self.__rss_skipDays |= set(days)
        return self.__rss_skipDays


    def webMaster(self, webMaster=None):
        """Get and set the person responsible for technical issues relating to
        the feed.

        :param webMaster: The person responsible for technical issues relating
            to the feed. This instance of Person must have its email set.
        :type webMaster: Person
        :returns: The person responsible for technical issues relating to the
            feed.
        """
        if webMaster is not None:
            if (not hasattr(webMaster, "email")) or not webMaster.email:
                raise ValueError("The webmaster must have an email attribute "
                                 "and it must be set and not empty.")
            self.__rss_webMaster = webMaster
        return self.__rss_webMaster

    def itunes_block(self, itunes_block=None):
        """Get or set the ITunes block attribute. Use this to prevent the entire
        podcast from appearing in the iTunes podcast directory.

        :param itunes_block: Block the podcast.
        :returns: If the podcast is blocked.
        """
        if not itunes_block is None:
            self.__itunes_block = itunes_block
        return self.__itunes_block

    def itunes_category(self, itunes_category=None, itunes_subcategory=None):
        """Get or set the ITunes category which appears in the category column
        and in iTunes Store Browser.

        The (sub-)category has to be one from the values defined at
        http://www.apple.com/itunes/podcasts/specs.html#categories

        :param itunes_category: Category of the podcast, unescaped.
        :type itunes_category: str
        :param itunes_subcategory: Subcategory of the podcast, unescaped. The subcategory need not be set.
        :type itunes_subcategory: str
        :returns: Dictionary which has category with key 'cat', and optionally subcategory with key 'sub'.
        """
        if not itunes_category is None:
            if not itunes_category in self._itunes_categories.keys():
                raise ValueError('Invalid category %s' % itunes_category)
            cat = {'cat': itunes_category}
            if not itunes_subcategory is None:
                if not itunes_subcategory in self._itunes_categories[itunes_category]:
                    raise ValueError('Invalid subcategory "%s" under category "%s"'
                                     % (itunes_subcategory, itunes_category))
                cat['sub'] = itunes_subcategory
            self.__itunes_category = cat
        return self.__itunes_category

    _itunes_categories = {
        'Arts': ['Design', 'Fashion & Beauty', 'Food', 'Literature',
                 'Performing Arts', 'Visual Arts'],
        'Business': ['Business News', 'Careers', 'Investing',
                     'Management & Marketing', 'Shopping'],
        'Comedy': [],
        'Education': ['Education', 'Education Technology',
                      'Higher Education', 'K-12', 'Language Courses', 'Training'],
        'Games & Hobbies': ['Automotive', 'Aviation', 'Hobbies',
                            'Other Games', 'Video Games'],
        'Government & Organizations': ['Local', 'National', 'Non-Profit',
                                       'Regional'],
        'Health': ['Alternative Health', 'Fitness & Nutrition', 'Self-Help',
                   'Sexuality'],
        'Kids & Family': [],
        'Music': [],
        'News & Politics': [],
        'Religion & Spirituality': ['Buddhism', 'Christianity', 'Hinduism',
                                    'Islam', 'Judaism', 'Other', 'Spirituality'],
        'Science & Medicine': ['Medicine', 'Natural Sciences',
                               'Social Sciences'],
        'Society & Culture': ['History', 'Personal Journals', 'Philosophy',
                              'Places & Travel'],
        'Sports & Recreation': ['Amateur', 'College & High School',
                                'Outdoor', 'Professional'],
        'Technology': ['Gadgets', 'Tech News', 'Podcasting',
                       'Software How-To'],
        'TV & Film': []
    }

    def itunes_image(self, itunes_image=None):
        """Get or set the image for the podcast. This tag specifies the artwork
        for your podcast. Put the URL to the image in the href attribute. iTunes
        prefers square .jpg images that are at least 1400x1400 pixels, which is
        different from what is specified for the standard RSS image tag. In order
        for a podcast to be eligible for an iTunes Store feature, the
        accompanying image must be at least 1400x1400 pixels.

        iTunes supports images in JPEG and PNG formats with an RGB color space
        (CMYK is not supported). The URL must end in ".jpg" or ".png". If the
        <itunes:image> tag is not present, iTunes will use the contents of the
        RSS image tag.

        If you change your podcast’s image, also change the file’s name. iTunes
        may not change the image if it checks your feed and the image URL is the
        same. The server hosting your cover art image must allow HTTP head
        requests for iTS to be able to automatically update your cover art.

        :param itunes_image: Image of the podcast.
        :type itunes_image: str
        :returns: Image of the podcast.
        """
        if not itunes_image is None:
            lowercase_itunes_image = itunes_image.lower()
            if not (lowercase_itunes_image.endswith(('.jpg', '.jpeg', '.png'))):
                raise ValueError('Image filename must end with png or jpg, not .%s' % itunes_image.split(".")[-1])
            self.__itunes_image = itunes_image
        return self.__itunes_image

    def itunes_explicit(self, itunes_explicit=None):
        """Get or the the itunes:explicit value of the podcast. This tag should
        be used to indicate whether your podcast contains explicit material. The
        three values for this tag are "yes", "no", and "clean".

        If you populate this tag with "yes", an "explicit" parental advisory
        graphic will appear next to your podcast artwork on the iTunes Store and
        in the Name column in iTunes. If the value is "clean", the parental
        advisory type is considered Clean, meaning that no explicit language or
        adult content is included anywhere in the episodes, and a "clean" graphic
        will appear. If the explicit tag is present and has any other value
        (e.g., "no"), you see no indicator — blank is the default advisory type.

        :param itunes_explicit: "yes" if the podcast contains explicit material, "clean" if it doesn't. "no" counts
            as blank.
        :type itunes_explicit: str
        :returns: If the podcast contains explicit material.
        """
        if not itunes_explicit is None:
            if not itunes_explicit in ('', 'yes', 'no', 'clean'):
                raise ValueError('Invalid value "%s" for explicit tag' % itunes_explicit)
            self.__itunes_explicit = itunes_explicit
        return self.__itunes_explicit

    def itunes_complete(self, itunes_complete=None):
        """Get or set the itunes:complete value of the podcast. This tag can be
        used to indicate the completion of a podcast.

        If you populate this tag with "yes", you are indicating that no more
        episodes will be added to the podcast. If the &lt;itunes:complete&gt; tag is
        present and has any other value (e.g. “no”), it will have no effect on
        the podcast.

        :param itunes_complete: If the podcast is complete.
        :type itunes_complete: bool or str
        :returns: If the podcast is complete.
        """
        if not itunes_complete is None:
            if not itunes_complete in ('yes', 'no', '', True, False):
                raise ValueError('Invalid value "%s" for complete tag' % itunes_complete)
            if itunes_complete == True:
                itunes_complete = 'yes'
            if itunes_complete == False:
                itunes_complete = 'no'
            self.__itunes_complete = itunes_complete
        return self.__itunes_complete

    def itunes_new_feed_url(self, itunes_new_feed_url=None):
        """Get or set the new-feed-url property of the podcast. This tag allows
        you to change the URL where the podcast feed is located

        After adding the tag to your old feed, you should maintain the old feed
        for 48 hours before retiring it. At that point, iTunes will have updated
        the directory with the new feed URL.

        :param itunes_new_feed_url: New feed URL.
        :type itunes_new_feed_url: str
        :returns: New feed URL.
        """
        if not itunes_new_feed_url is None:
            self.__itunes_new_feed_url = itunes_new_feed_url
        return self.__itunes_new_feed_url

    def itunes_owner(self, owner):
        """Get or set the itunes:owner of the podcast. This tag contains
        information that will be used to contact the owner of the podcast for
        communication specifically about the podcast. It will not be publicly
        displayed.

        Both the name and email are required; you cannot use one or the other alone.

        :param owner: The person which iTunes will contact when needed.
        :returns: The owner of this feed, which iTunes will contact when needed.
        """
        if owner is not None:
            if owner.name and owner.email:
                self.__itunes_owner = owner
            else:
                raise ValueError('Both name and email must be set.')
        return self.__itunes_owner

    def itunes_subtitle(self, itunes_subtitle=None):
        """Get or set the itunes:subtitle value for the podcast. The contents of
        this tag are shown in the Description column in iTunes. The subtitle
        displays best if it is only a few words long.

        :param itunes_subtitle: Subtitle of the podcast.
        :type itunes_subtitle: str
        :returns: Subtitle of the podcast.
        """
        if not itunes_subtitle is None:
            self.__itunes_subtitle = itunes_subtitle
        return self.__itunes_subtitle

    def feed_url(self, feed_url=None):
        """Get or set the URL which this feed is available at.

        Identifying a feed's URL within the feed makes it more portable,
        self-contained, and easier to cache. You should therefore set this
        property, if you're able to.

        :param feed_url: The URL at which you can access this feed.
        :type feed_url: str
        :returns: The URL at which you can access this feed.
        """
        if feed_url is not None:
            if feed_url and not feed_url.startswith((
                    'http://',
                    'https://',
                    'ftp://',
                    'news://')):
                raise ValueError("The feed url must be a valid URL, but it "
                                 "doesn't have a valid URL scheme "
                                 "(like for example http:// or https://)")
            self.__self_link = feed_url
        return self.__self_link

