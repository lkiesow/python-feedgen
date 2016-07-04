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
from feedgen.episode import BaseEpisode
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

    The following attributes are mandatory:

    * :attr:`~feedgen.podcast.Podcast.name`
    * :attr:`~feedgen.podcast.Podcast.website`
    * :attr:`~feedgen.podcast.Podcast.description`
    * :attr:`~feedgen.podcast.Podcast.explicit`
    """


    def __init__(self):
        self.__episodes = []
        """The list used by self.episodes."""
        self.__episode_class = BaseEpisode
        """The internal value used by self.Episode."""

        ## RSS
        # http://www.rssboard.org/rss-specification
        # Mandatory:
        self.__name = None
        self.__website = None
        self.__description = None
        self.__explicit = None

        # Optional:
        self.__cloud = None
        self.__copyright = None
        self.__docs = 'http://www.rssboard.org/rss-specification'
        self.__generator = self._feedgen_generator_str
        self.__language = None
        self.__last_updated = None
        self.__authors = []
        self.__publication_date = None
        self.__skip_hours = None
        self.__skip_days = None
        self.__web_master = None

        self.__feed_url = None

        ## ITunes tags
        # http://www.apple.com/itunes/podcasts/specs.html#rss
        self.__withhold_from_itunes = False
        self.__category = None
        self.__image = None
        self.__complete = None
        self.__new_feed_url = None
        self.__owner = None
        self.__subtitle = None

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
            >>> from feedgen.podcast import Podcast
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
        if not (self.__name and self.__website and self.__description
                and self.__explicit is not None):
            missing = ', '.join(([] if self.__name else ['title']) +
                                ([] if self.__website else ['link']) +
                                ([] if self.__description else ['description']) +
                                ([] if self.__explicit else ['itunes_explicit']))
            raise ValueError('Required fields not set (%s)' % missing)
        title = etree.SubElement(channel, 'title')
        title.text = self.__name
        link = etree.SubElement(channel, 'link')
        link.text = self.__website
        desc = etree.SubElement(channel, 'description')
        desc.text = self.__description
        explicit = etree.SubElement(channel, '{%s}explicit' % ITUNES_NS)
        explicit.text = "yes" if self.__explicit else "no"

        if self.__cloud:
            cloud = etree.SubElement(channel, 'cloud')
            cloud.attrib['domain'] = self.__cloud.get('domain')
            cloud.attrib['port'] = str(self.__cloud.get('port'))
            cloud.attrib['path'] = self.__cloud.get('path')
            cloud.attrib['registerProcedure'] = self.__cloud.get(
                    'registerProcedure')
            cloud.attrib['protocol'] = self.__cloud.get('protocol')
        if self.__copyright:
            copyright = etree.SubElement(channel, 'copyright')
            copyright.text = self.__copyright
        if self.__docs:
            docs = etree.SubElement(channel, 'docs')
            docs.text = self.__docs
        if self.__generator:
            generator = etree.SubElement(channel, 'generator')
            generator.text = self.__generator
        if self.__language:
            language = etree.SubElement(channel, 'language')
            language.text = self.__language

        if self.__last_updated is None:
            lastBuildDateDate = datetime.now(dateutil.tz.tzutc())
        else:
            lastBuildDateDate = self.__last_updated
        if lastBuildDateDate:
            lastBuildDate = etree.SubElement(channel, 'lastBuildDate')
            lastBuildDate.text = formatRFC2822(lastBuildDateDate)

        if self.__authors:
            authors_with_name = [a.name for a in self.__authors if a.name]
            if authors_with_name:
                # We have something to display as itunes:author, combine all
                # names
                itunes_author = \
                    etree.SubElement(channel, '{%s}author' % ITUNES_NS)
                itunes_author.text = listToHumanreadableStr(authors_with_name)
            if len(self.__authors) > 1 or not self.__authors[0].email:
                # Use dc:creator, since it supports multiple authors (and
                # author without email)
                for a in self.__authors or []:
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
                author.text = str(self.__authors[0])

        if self.__publication_date is None:
            episode_dates = [e.publication_date() for e in self.episodes
                             if e.publication_date() is not None]
            if episode_dates:
                actual_pubDate = max(episode_dates)
            else:
                actual_pubDate = None
        else:
            actual_pubDate = self.__publication_date
        if actual_pubDate:
            pubDate = etree.SubElement(channel, 'pubDate')
            pubDate.text = formatRFC2822(actual_pubDate)

        if self.__skip_hours:
            skipHours = etree.SubElement(channel, 'skipHours')
            for h in self.__skip_hours:
                hour = etree.SubElement(skipHours, 'hour')
                hour.text = str(h)
        if self.__skip_days:
            skipDays = etree.SubElement(channel, 'skipDays')
            for d in self.__skip_days:
                day = etree.SubElement(skipDays, 'day')
                day.text = d
        if self.__web_master:
            if not self.__web_master.email:
                raise RuntimeError("webMaster must have an email. Did you "
                                   "set email to None after assigning that "
                                   "Person to webMaster?")
            webMaster = etree.SubElement(channel, 'webMaster')
            webMaster.text = str(self.__web_master)

        if self.__withhold_from_itunes:
            block = etree.SubElement(channel, '{%s}block' % ITUNES_NS)
            block.text = 'Yes'

        if self.__category:
            category = etree.SubElement(channel, '{%s}category' % ITUNES_NS)
            category.attrib['text'] = self.__category.category
            if self.__category.subcategory:
                subcategory = etree.SubElement(category, '{%s}category' % ITUNES_NS)
                subcategory.attrib['text'] = self.__category.subcategory

        if self.__image:
            image = etree.SubElement(channel, '{%s}image' % ITUNES_NS)
            image.attrib['href'] = self.__image

        if self.__complete in ('yes', 'no'):
            complete = etree.SubElement(channel, '{%s}complete' % ITUNES_NS)
            complete.text = self.__complete

        if self.__new_feed_url:
            new_feed_url = etree.SubElement(channel, '{%s}new-feed-url' % ITUNES_NS)
            new_feed_url.text = self.__new_feed_url

        if self.__owner:
            owner = etree.SubElement(channel, '{%s}owner' % ITUNES_NS)
            owner_name = etree.SubElement(owner, '{%s}name' % ITUNES_NS)
            owner_name.text = self.__owner.name
            owner_email = etree.SubElement(owner, '{%s}email' % ITUNES_NS)
            owner_email.text = self.__owner.email

        if self.__subtitle:
            subtitle = etree.SubElement(channel, '{%s}subtitle' % ITUNES_NS)
            subtitle.text = self.__subtitle

        if self.__feed_url:
            link_to_self = etree.SubElement(channel, '{%s}link' % nsmap['atom'])
            link_to_self.attrib['href'] = self.__feed_url
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

        This will set rss:title.

        :param name: The new name of the podcast.
        :type name: str
        :returns: The podcast's name.
        """
        if not name is None:
            self.__name = name
        return self.__name


    def last_updated(self, last_updated=None):
        """Set or get the updated value which indicates the last time the feed
        was modified in a significant way. Most often, it is taken to mean the
        last time the feed was generated, which is why it defaults to the
        time and date at which the RSS is generated, if set to None.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        This will set rss:lastBuildDate.

        Default value
            If not set, updated has as value the current date and time.

        Set this to False to have no updated value in the feed.

        :param last_updated: The modification date.
        :type last_updated: str or datetime.datetime
        :returns: Modification date as datetime.datetime
        """
        if not last_updated is None:
            if last_updated is False:
                self.__last_updated = False
            else:
                if isinstance(last_updated, string_types):
                    last_updated = dateutil.parser.parse(last_updated)
                if not isinstance(last_updated, datetime):
                    raise ValueError('Invalid datetime format')
                if last_updated.tzinfo is None:
                    raise ValueError('Datetime object has no timezone info')
                self.__last_updated = last_updated

        return self.__last_updated


    def website(self, href=None):
        """Get or set this podcast's website.

        This corresponds to the RSS link element.

        :param href: URI of this podcast's website.

        Example::

            >>> p.website( href='http://example.com/')

        """
        if not href is None:
            self.__website = href
        return self.__website


    def cloud(self, domain=None, port=None, path=None, registerProcedure=None,
            protocol=None):
        """Set or get the cloud data of the feed. It specifies a web service
        that supports the rssCloud interface which can be implemented in
        HTTP-POST, XML-RPC or SOAP 1.1.

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
            self.__cloud = {'domain':domain, 'port':port, 'path':path,
                    'registerProcedure':registerProcedure, 'protocol':protocol}
        return self.__cloud


    def generator(self, generator=None, version=None, uri=None,
                  exclude_feedgen=False):
        """Get or set the generator of the feed, which identifies the software
        used to generate the feed, for debugging and other purposes.

        :param generator: Software used to create the feed.
        :param version: (Optional) Version of the software, as a tuple.
        :param uri: (Optional) URI the software can be found.
        :param exclude_feedgen: (Optional) Set to True to disable the mentioning
            of the python-feedgen library.
        """
        if not generator is None:
            self.__generator = self._program_name_to_str(generator, version, uri) + \
                               (" (using %s)" % self._feedgen_generator_str
                                    if not exclude_feedgen else "")
        return self.__generator

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
            self.__copyright = copyright
        return self.__copyright


    def description(self, description=None):
        """Set and get the description of the feed,
        which is a phrase or sentence describing the channel. It is mandatory for
        RSS feeds, and is shown under the podcast's name on the iTunes store
        page.

        :param description: Description of the podcast.
        :returns: Description of the podcast.

        """
        if not description is None:
            self.__description = description
        return self.__description


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
            self.__language = language
        return self.__language


    @property
    def authors(self):
        """List of :class:`~feedgen.person.Person` that are responsible for this
        podcast's editorial content.

        Any value you assign to authors will be automatically converted to a
        list, but only if it's iterable (like tuple, set and so on). It is an
        error to assign a single :class:`~feedgen.person.Person` object to this
        attribute::

            >>> # This results in an error
            >>> p.authors = Person("John Doe", "johndoe@example.org")
            TypeError: Only iterable types can be assigned to authors, ...
            >>> # This is the correct way:
            >>> p.authors = [Person("John Doe", "johndoe@example.org")]

        The authors don't need to have both name and email set. The names are
        shown under the podcast's title on iTunes.

        The initial value is an empty list, so you can use the list methods
        right away.

        Example::

            >>> # This attribute is just a list - you can for example append:
            >>> p.authors.append(Person("John Doe", "johndoe@example.org"))
            >>> # Or they can be given as new list (overriding earlier authors)
            >>> p.authors = [Person("John Doe", "johndoe@example.org"),
            ...               Person("Mary Sue", "marysue@example.org")]
        """
        return self.__authors

    @authors.setter
    def authors(self, authors):
        try:
            self.__authors = list(authors)
        except TypeError:
            raise TypeError("Only iterable types can be assigned to authors, "
                            "%s given. You must put your object in a list, "
                            "even if there's only one author." % authors)


    def publication_date(self, publication_date=None):
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

        :param publication_date: The publication date.
        :returns: Publication date as datetime.datetime
        """
        if not publication_date is None:
            if isinstance(publication_date, string_types):
                publication_date = dateutil.parser.parse(publication_date)
            if publication_date is not False and not isinstance(publication_date, datetime):
                raise ValueError('Invalid datetime format')
            elif publication_date is not False and publication_date.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__publication_date = publication_date

        return self.__publication_date


    def skip_hours(self, hours=None, replace=False):
        """Set or get which hours feed readers don't need to refresh this feed.

        This method can be called with an hour or a list of hours. The hours are
        represented as integer values from 0 to 23. When called multiple times,
        the new hours are added to the list of existing hours, unless replace
        is True.

        For example, to skip hours between 18 and 7::

            >>> from feedgen.podcast import Podcast
            >>> p = Podcast()
            >>> p.skip_hours(range(18, 24))
            {18, 19, 20, 21, 22, 23}
            >>> p.skip_hours(range(8))
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
            if replace or not self.__skip_hours:
                self.__skip_hours = set()
            self.__skip_hours |= set(hours)
        return self.__skip_hours


    def skip_days(self, days=None, replace=False):
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
            if replace or not self.__skip_days:
                self.__skip_days = set()
            self.__skip_days |= set(days)
        return self.__skip_days


    def web_master(self, web_master=None):
        """Get and set the :class:`~feedgen.person.Person` responsible for
        technical issues relating to the feed.

        :param web_master: The person responsible for technical issues relating
            to the feed. This instance of Person must have its email set.
        :type web_master: Person
        :returns: The person responsible for technical issues relating to the
            feed.
        """
        if web_master is not None:
            if (not hasattr(web_master, "email")) or not web_master.email:
                raise ValueError("The webmaster must have an email attribute "
                                 "and it must be set and not empty.")
            self.__web_master = web_master
        return self.__web_master

    def withhold_from_itunes(self, withhold_from_itunes=None):
        """Get or set the iTunes block attribute. Use this to prevent the entire
        podcast from appearing in the iTunes podcast directory.

        Note that this will affect more than iTunes, since most podcatchers use
        the iTunes catalogue to implement the search feature. Listeners will
        still be able to subscribe by adding the feed's address manually.

        If you don't intend on submitting this podcast to iTunes, you can set
        this to True as a way of showing iTunes the middle finger (and prevent
        others from submitting it as well).

        Set it to ``True`` to withhold the entire podcast from iTunes. It is set
        to ``False`` by default, of course.

        :param withhold_from_itunes: ``True`` to block the podcast from iTunes.
        :type withhold_from_itunes: bool or None
        :returns: If the podcast is blocked.
        """
        if not withhold_from_itunes is None:
            self.__withhold_from_itunes = withhold_from_itunes
        return self.__withhold_from_itunes

    def category(self, category=None):
        """Get or set the iTunes category, which appears in the category column
        and in iTunes Store Browser.

        Use the :class:`feedgen.category.Category` class.

        :param category: This podcast's category.
        :type category: feedgen.category.Category or None
        :returns: This podcast's category.
        """
        if not category is None:
            # Check that the category quacks like a duck
            if hasattr(category, "category") and \
                    hasattr(category, "subcategory"):
                self.__category = category
            else:
                raise TypeError("A Category(-like) object must be used, got "
                                "%s" % category)
        return self.__category


    def image(self, image=None):
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

        :param image: Image of the podcast.
        :type image: str
        :returns: Image of the podcast.
        """
        if not image is None:
            lowercase_itunes_image = image.lower()
            if not (lowercase_itunes_image.endswith(('.jpg', '.jpeg', '.png'))):
                raise ValueError('Image filename must end with png or jpg, not .%s' % image.split(".")[-1])
            self.__image = image
        return self.__image

    def explicit(self, explicit=None):
        """Get or set whether this podcast may be inappropriate for children or
        not.

        This is one of the mandatory attributes, and can seen as the
        default for episodes. Individual episodes can be marked as explicit
        or clean independently from the podcast.

        If you set this to ``True``, an "explicit" parental advisory
        graphic will appear next to your podcast artwork on the iTunes Store and
        in the Name column in iTunes. If it is set to ``False``,
        the parental advisory type is considered Clean, meaning that no explicit
        language or adult content is included anywhere in the episodes, and a
        "clean" graphic will appear.

        :param explicit: True if explicit, False if not.
        :type explicit: bool or None
        :returns: Whether the podcast contains explicit material or not.
        """
        if not explicit is None:
            self.__explicit = explicit
        return self.__explicit

    def complete(self, complete=None):
        """Get or set the itunes:complete value of the podcast. This tag can be
        used to indicate the completion of a podcast.

        If you populate this tag with "yes", you are indicating that no more
        episodes will be added to the podcast. If the <itunes:complete> tag is
        present and has any other value (e.g. “no”), it will have no effect on
        the podcast.

        .. warning::

            Setting this to ``True`` is the same as promising you'll never ever
            release a new episode. Do NOT set this to ``True`` as long as
            there's any chance at all that a new episode will be released
            someday.

        :param complete: If the podcast is complete.
        :type complete: bool or str
        :returns: If the podcast is complete.
        """
        if not complete is None:
            if not complete in ('yes', 'no', '', True, False):
                raise ValueError('Invalid value "%s" for complete tag' % complete)
            if complete == True:
                complete = 'yes'
            if complete == False:
                complete = 'no'
            self.__complete = complete
        return self.__complete

    def new_feed_url(self, new_feed_url=None):
        """Get or set the itunes-new-feed-url property of the podcast. This tag allows
        you to change the URL where the podcast feed is located

        After adding the tag to your old feed, you should maintain the old feed
        for 48 hours before retiring it. At that point, iTunes will have updated
        the directory with the new feed URL.

        .. warning::

            iTunes supports this mechanic of changing your feed's location.
            However, you cannot assume the same of everyone else who has
            subscribed to this podcast. Therefore, you should NEVER stop
            supporting an old location for your podcast. Instead, you should
            create redirects so those with the old address are redirected to
            your new address, and keep those up for all eternity.

        .. warning::

            Make sure the new URL here is correct, or else you're making
            people switch to a URL that doesn't work!

        :param new_feed_url: New feed URL.
        :type new_feed_url: str
        :returns: New feed URL.
        """
        if not new_feed_url is None:
            self.__new_feed_url = new_feed_url
        return self.__new_feed_url

    def owner(self, owner):
        """Get or set the owner of the podcast. This tag contains
        information that iTunes will use to contact the owner of the podcast for
        communication specifically about the podcast. It will not be publicly
        displayed, but it will be in the feed source.

        Both the name and email are required.

        :param owner: The :class:`~feedgen.person.Person` which iTunes will
            contact when needed.
        :returns: The owner of this feed, which iTunes will contact when needed.
        """
        if owner is not None:
            if owner.name and owner.email:
                self.__owner = owner
            else:
                raise ValueError('Both name and email must be set.')
        return self.__owner

    def subtitle(self, subtitle=None):
        """Get or set the itunes:subtitle value for the podcast. The contents of
        this tag are shown in the Description column in iTunes. The subtitle
        displays best if it is only a few words long.

        :param subtitle: Subtitle of the podcast.
        :type subtitle: str
        :returns: Subtitle of the podcast.
        """
        if not subtitle is None:
            self.__subtitle = subtitle
        return self.__subtitle

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
            self.__feed_url = feed_url
        return self.__feed_url

