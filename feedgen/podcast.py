# -*- coding: utf-8 -*-
"""
    feedgen.feed
    ~~~~~~~~~~~~

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.

"""
from future.utils import iteritems
from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from feedgen.episode import Episode
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

    * :attr:`~feedgen.Podcast.name`
    * :attr:`~feedgen.Podcast.website`
    * :attr:`~feedgen.Podcast.description`
    * :attr:`~feedgen.Podcast.explicit`

    There is a **shortcut** you can use when creating new Podcast objects, that
    lets you populate the attributes using the constructor. Use keyword
    arguments with the **attribute name as keyword** and the desired value as
    value::

        >>> import feedgen
        >>> # The following...
        >>> p = Podcast()
        >>> p.name = "The Test Podcast"
        >>> p.website = "http://example.com"
        >>> # ...is the same as this:
        >>> p = Podcast(
        ...     name="The Test Podcast",
        ...     website="http://example.com",
        ... )

    Of course, you can do this for as many (or few) attributes as you like, and
    you can still set the attributes afterwards, like always.

    :raises: TypeError if you use a keyword which isn't recognized as an
        attribute. ValueError if you use a value which isn't compatible with
        the attribute (just like when you assign it manually).

    """

    def __init__(self, **kwargs):
        self.__episodes = []
        """The list used by self.episodes."""
        self.__episode_class = Episode
        """The internal value used by self.Episode."""

        ## RSS
        # http://www.rssboard.org/rss-specification
        # Mandatory:
        self.name = None
        """The name of the podcast. It should be a human
        readable title. Often the same as the title of the
        associated website. This is mandatory for RSS and must
        not be blank.

        This will set rss:title.
        """

        self.website = None
        """This podcast's website's absolute URL.

        One of the mandatory attributes.

        This corresponds to the RSS link element.
        """

        self.description = None
        """The description of the feed, which is a phrase or sentence describing
        the channel. It is mandatory for RSS feeds, and is shown under the
        podcast's name on the iTunes store page."""

        self.explicit = None
        """Whether this podcast may be inappropriate for children or not.

        This is one of the mandatory attributes, and can seen as the
        default for episodes. Individual episodes can be marked as explicit
        or clean independently from the podcast.

        If you set this to ``True``, an "explicit" parental advisory
        graphic will appear next to your podcast artwork on the iTunes Store and
        in the Name column in iTunes. If it is set to ``False``,
        the parental advisory type is considered Clean, meaning that no explicit
        language or adult content is included anywhere in the episodes, and a
        "clean" graphic will appear."""

        # Optional:
        self.__cloud = None

        self.copyright = None
        """The copyright notice for content in this podcast.

        This should be human-readable. For example, "Copyright 2016 Example
        Radio".

        Note that even if you leave out the copyright notice, your content is
        still protected by copyright (unless anything else is indicated), since
        you do not need a copyright statement for something to be protected by
        copyright. If you intend to put the podcast in public domain or license
        it under a Creative Commons license, you should say so in the copyright
        notice."""

        self.__docs = 'http://www.rssboard.org/rss-specification'

        self.generator = self._feedgen_generator_str
        """A string identifying the software that generated this RSS feed.
        Defaults to a string identifying PodcastGenerator.

        .. seealso::

           The :py:meth:`.set_generator` method
              A convenient way to set the generator value and include version
              and url.
        """

        self.language = None
        """The language of the podcast.

        This allows aggregators to group all Italian
        language podcasts, for example, on a single page.

        It must be a two-letter code, as found in ISO639-1, with the
        possibility of specifying subcodes (eg. en-US for American English).
        See http://www.rssboard.org/rss-language-codes and
        http://www.loc.gov/standards/iso639-2/php/code_list.php"""

        self.__last_updated = None

        self.__authors = []

        self.__publication_date = None

        self.__skip_hours = None

        self.__skip_days = None

        self.__web_master = None

        self.__feed_url = None

        ## ITunes tags
        # http://www.apple.com/itunes/podcasts/specs.html#rss
        self.withhold_from_itunes = False
        """Prevent the entire podcast from appearing in the iTunes podcast
        directory.

        Note that this will affect more than iTunes, since most podcatchers use
        the iTunes catalogue to implement the search feature. Listeners will
        still be able to subscribe by adding the feed's address manually.

        If you don't intend on submitting this podcast to iTunes, you can set
        this to True as a way of showing iTunes the middle finger (and prevent
        others from submitting it as well).

        Set it to ``True`` to withhold the entire podcast from iTunes. It is set
        to ``False`` by default, of course.

        :type: bool"""

        self.__category = None

        self.__image = None

        self.__complete = None

        self.new_feed_url = None
        """When set, tell iTunes that your feed has moved to this URL.

        After adding the tag to your old feed, you should maintain the old feed
        for 48 hours before retiring it. At that point, iTunes will have updated
        the directory with the new feed URL.

        .. warning::

            iTunes supports this mechanic of changing your feed's location.
            However, you cannot assume the same of everyone else who has
            subscribed to this podcast. Therefore, you should NEVER stop
            supporting an old location for your podcast. Instead, you should
            create HTTP redirects so those with the old address are redirected
            to your new address, and keep those redirects up for all eternity.

        .. warning::

            Make sure the new URL here is correct, or else you're making
            people switch to a URL that doesn't work!
        """

        self.__owner = None

        self.subtitle = None
        """The subtitle for your podcast, shown mainly as a very short
        description on iTunes. The subtitle displays best if it is only a few
        words long, like a short slogan."""

        # Populate the podcast with the keyword arguments
        for attribute, value in iteritems(kwargs):
            if hasattr(self, attribute):
                setattr(self, attribute, value)
            else:
                raise TypeError("Keyword argument %s (with value %s) doesn't "
                                "match any attribute in Podcast." %
                                (attribute, value))


    @property
    def episodes(self):
        """List of episodes that are part of this podcast.

        See :py:meth:`.add_episode` for an easy way to create new episodes and
        assign them to this podcast in one call.
        """
        return self.__episodes

    @episodes.setter
    def episodes(self, episodes):
        # Ensure it is a list
        self.__episodes = list(episodes) if not isinstance(episodes, list) \
            else episodes

    @property
    def episode_class(self):
        """Class used to represent episodes.

        This is used by :py:meth:`.add_episode` when creating new episode
        objects, and you may use it too when creating episodes.

        By default, this property points to :py:class:`Episode`.

        When assigning a new class to ``episode_class``, you must make sure the
        new value (1) is a class and not an instance, and (2) is a subclass of
        Episode (or is Episode itself).

        Example of use::

            >>> # Create new podcast
            >>> from feedgen import Podcast, Episode
            >>> p = Podcast()
            >>> # Normal way of creating new episodes
            >>> episode1 = Episode()
            >>> p.episodes.append(episode1)
            >>> # Or use add_episode (and thus episode_class indirectly)
            >>> episode2 = p.add_episode()
            >>> # Or use episode_class directly
            >>> episode3 = p.episode_class()
            >>> p.episodes.append(episode3)
            >>> # Say you want to use AlternateEpisode class instead of Episode
            >>> from mymodule import AlternateEpisode
            >>> p.episode_class = AlternateEpisode
            >>> episode4 = p.add_episode()
            >>> episode4.title("This is an instance of AlternateEpisode!")
        """
        return self.__episode_class

    @episode_class.setter
    def episode_class(self, value):
        if not inspect.isclass(value):
            raise ValueError("New episode_class must NOT be an _instance_ of "
                             "the desired class, but rather the class itself. "
                             "You can generally achieve this by removing the "
                             "parenthesis from the constructor call. For "
                             "example, use Episode, not Episode().")
        elif issubclass(value, Episode):
            self.__episode_class = value
        else:
            raise ValueError("New episode_class must be Episode or a descendant"
                             " of it (so the API still works).")

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

        Internally, this method creates a new instance of
        :attr:`~feedgen.Episode.episode_class`, which means you can change what
        type of objects are created by changing
        :attr:`~feedgen.Episode.episode_class`.

        """
        if new_episode is None:
            new_episode = self.episode_class()
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
        if not (self.name and self.website and self.description
                and self.explicit is not None):
            missing = ', '.join(([] if self.name else ['title']) +
                                ([] if self.website else ['link']) +
                                ([] if self.description else ['description']) +
                                ([] if self.explicit else ['itunes_explicit']))
            raise ValueError('Required fields not set (%s)' % missing)
        title = etree.SubElement(channel, 'title')
        title.text = self.name
        link = etree.SubElement(channel, 'link')
        link.text = self.website
        desc = etree.SubElement(channel, 'description')
        desc.text = self.description
        explicit = etree.SubElement(channel, '{%s}explicit' % ITUNES_NS)
        explicit.text = "yes" if self.explicit else "no"

        if self.__cloud:
            cloud = etree.SubElement(channel, 'cloud')
            cloud.attrib['domain'] = self.__cloud.get('domain')
            cloud.attrib['port'] = str(self.__cloud.get('port'))
            cloud.attrib['path'] = self.__cloud.get('path')
            cloud.attrib['registerProcedure'] = self.__cloud.get(
                    'registerProcedure')
            cloud.attrib['protocol'] = self.__cloud.get('protocol')
        if self.copyright:
            copyright = etree.SubElement(channel, 'copyright')
            copyright.text = self.copyright
        if self.__docs:
            docs = etree.SubElement(channel, 'docs')
            docs.text = self.__docs
        if self.generator:
            generator = etree.SubElement(channel, 'generator')
            generator.text = self.generator
        if self.language:
            language = etree.SubElement(channel, 'language')
            language.text = self.language

        if self.last_updated is None:
            lastBuildDateDate = datetime.now(dateutil.tz.tzutc())
        else:
            lastBuildDateDate = self.last_updated
        if lastBuildDateDate:
            lastBuildDate = etree.SubElement(channel, 'lastBuildDate')
            lastBuildDate.text = formatRFC2822(lastBuildDateDate)

        if self.authors:
            authors_with_name = [a.name for a in self.authors if a.name]
            if authors_with_name:
                # We have something to display as itunes:author, combine all
                # names
                itunes_author = \
                    etree.SubElement(channel, '{%s}author' % ITUNES_NS)
                itunes_author.text = listToHumanreadableStr(authors_with_name)
            if len(self.authors) > 1 or not self.authors[0].email:
                # Use dc:creator, since it supports multiple authors (and
                # author without email)
                for a in self.authors or []:
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
                author.text = str(self.authors[0])

        if self.publication_date is None:
            episode_dates = [e.publication_date for e in self.episodes
                             if e.publication_date is not None]
            if episode_dates:
                actual_pubDate = max(episode_dates)
            else:
                actual_pubDate = None
        else:
            actual_pubDate = self.publication_date
        if actual_pubDate:
            pubDate = etree.SubElement(channel, 'pubDate')
            pubDate.text = formatRFC2822(actual_pubDate)

        if self.skip_hours:
            skipHours = etree.SubElement(channel, 'skipHours')
            for h in self.skip_hours:
                hour = etree.SubElement(skipHours, 'hour')
                hour.text = str(h)
        if self.skip_days:
            skipDays = etree.SubElement(channel, 'skipDays')
            for d in self.skip_days:
                day = etree.SubElement(skipDays, 'day')
                day.text = d
        if self.web_master:
            if not self.web_master.email:
                raise RuntimeError("webMaster must have an email. Did you "
                                   "set email to None after assigning that "
                                   "Person to webMaster?")
            webMaster = etree.SubElement(channel, 'webMaster')
            webMaster.text = str(self.web_master)

        if self.withhold_from_itunes:
            block = etree.SubElement(channel, '{%s}block' % ITUNES_NS)
            block.text = 'Yes'

        if self.category:
            category = etree.SubElement(channel, '{%s}category' % ITUNES_NS)
            category.attrib['text'] = self.category.category
            if self.category.subcategory:
                subcategory = etree.SubElement(category, '{%s}category' % ITUNES_NS)
                subcategory.attrib['text'] = self.category.subcategory

        if self.image:
            image = etree.SubElement(channel, '{%s}image' % ITUNES_NS)
            image.attrib['href'] = self.image

        if self.complete:
            complete = etree.SubElement(channel, '{%s}complete' % ITUNES_NS)
            complete.text = "Yes"

        if self.new_feed_url:
            new_feed_url = etree.SubElement(channel, '{%s}new-feed-url' % ITUNES_NS)
            new_feed_url.text = self.new_feed_url

        if self.owner:
            owner = etree.SubElement(channel, '{%s}owner' % ITUNES_NS)
            owner_name = etree.SubElement(owner, '{%s}name' % ITUNES_NS)
            owner_name.text = self.owner.name
            owner_email = etree.SubElement(owner, '{%s}email' % ITUNES_NS)
            owner_email.text = self.owner.email

        if self.subtitle:
            subtitle = etree.SubElement(channel, '{%s}subtitle' % ITUNES_NS)
            subtitle.text = self.subtitle

        if self.feed_url:
            link_to_self = etree.SubElement(channel, '{%s}link' % nsmap['atom'])
            link_to_self.attrib['href'] = self.feed_url
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

    @property
    def last_updated(self):
        """The last time the feed was modified in a significant way. Most often,
        it is taken to mean the last time the feed was generated, which is why
        it defaults to the time and date at which the RSS is generated, if set
        to None. The default should be sufficient for most, if not all, use
        cases.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        This corresponds to rss:lastBuildDate. Set this to False to have no
        lastBuildDate element in the feed (and thus suppress the default).

        :type: :obj:`str`, :class:`datetime.datetime` or :obj:`None`.
        """
        return self.__last_updated

    @last_updated.setter
    def last_updated(self, last_updated):
        if last_updated is None or last_updated is False:
            self.__last_updated = last_updated
        else:
            if isinstance(last_updated, string_types):
                last_updated = dateutil.parser.parse(last_updated)
            if not isinstance(last_updated, datetime):
                raise ValueError('Invalid datetime format')
            if last_updated.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__last_updated = last_updated

    @property
    def cloud(self):
        """The cloud data of the feed, as a 5-tuple. It specifies a web service
        that supports the rssCloud interface which can be implemented in
        HTTP-POST, XML-RPC or SOAP 1.1.

        The tuple should look like this: ``(domain, port, path, registerProcedure,
        protocol)``.

        :domain: The domain where the webservice can be found.
        :port: The port the webservice listens to.
        :path: The path of the webservice.
        :registerProcedure: The procedure to call.
        :protocol: Can be either "HTTP-POST", "xml-rpc" or "soap".

        Example::

            p.cloud = ("podcast.example.org", 80, "/rpc", "cloud.notify",
                       "xml-rpc")

        .. tip::

            PubSubHubbub is a competitor to rssCloud, and is the preferred
            choice if you're looking to set up a new service of this kind.
        """
        tuple_keys = ['domain', 'port', 'path', 'registerProcedure', 'protocol']
        return tuple(self.__cloud[key] for key in tuple_keys) if self.__cloud \
            else self.__cloud

    @cloud.setter
    def cloud(self, cloud):
        if cloud is not None:
            try:
                domain, port, path, registerProcedure, protocol = cloud
            except ValueError:
                raise TypeError("Value of cloud must either be None or a "
                                "5-tuple.")
            if not (domain and (port != False) and path and registerProcedure
                    and protocol):
                raise ValueError("All parameters of cloud must be present and"
                                 " not empty.")
            self.__cloud = {'domain':domain, 'port':port, 'path':path,
                    'registerProcedure':registerProcedure, 'protocol':protocol}
        else:
            self.__cloud = None

    def set_generator(self, generator=None, version=None, uri=None,
                  exclude_feedgen=False):
        """Set the generator of the feed, formatted nicely, which identifies the
        software used to generate the feed, for debugging and other purposes.

        :param generator: Software used to create the feed.
        :param version: (Optional) Version of the software, as a tuple.
        :param uri: (Optional) URI the software can be found.
        :param exclude_feedgen: (Optional) Set to True to disable the mentioning
            of the python-feedgen library.

        .. seealso::

           The attribute :py:attr:`.generator`
              Lets you access and set the generator string yourself, without
              any formatting help.
        """
        self.generator = self._program_name_to_str(generator, version, uri) + \
                         (" (using %s)" % self._feedgen_generator_str
                                if not exclude_feedgen else "")

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


    @property
    def authors(self):
        """List of :class:`~feedgen.Person` that are responsible for this
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

    @property
    def publication_date(self):
        """Set or get the publication date for the content in the channel. For
        example, the New York Times publishes on a daily basis, the publication
        date flips once every 24 hours. That's when the publication date of the
        channel changes.

        :type: None, a string which will automatically be parsed or a
           datetime.datetime object. In any case it is necessary that the value
           include timezone information.
        :Default value: If this is None when the feed is generated, the
           publication date of the episode with the latest publication date (which
           may be in the future) is used. If there are no episodes, the publication
           date is omitted from the feed.

        If you want to forcefully omit the publication date from the feed, set
        this to ``False``.
        """
        return self.__publication_date

    @publication_date.setter
    def publication_date(self, publication_date):
        if publication_date is not None and publication_date is not False:
            if isinstance(publication_date, string_types):
                publication_date = dateutil.parser.parse(publication_date)
            if not isinstance(publication_date, datetime):
                raise ValueError('Invalid datetime format')
            elif publication_date.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
        self.__publication_date = publication_date

    @property
    def skip_hours(self):
        """Set of hours in which feed readers don't need to refresh this feed.

        The hours are represented as integer values from 0 to 23.

        For example, to skip hours between 18 and 7::

            >>> from feedgen import Podcast
            >>> p = Podcast()
            >>> p.skip_hours = set(range(18, 24))
            >>> p.skip_hours
            {18, 19, 20, 21, 22, 23}
            >>> p.skip_hours |= set(range(8))
            >>> p.skip_hours
            {0, 1, 2, 3, 4, 5, 6, 7, 18, 19, 20, 21, 22, 23}
        """
        return self.__skip_hours

    @skip_hours.setter
    def skip_hours(self, hours):
        if hours is not None:
            if not (isinstance(hours, list) or isinstance(hours, set)):
                hours = set(hours)
            for h in hours:
                if h not in range(24):
                    raise ValueError('Invalid hour %s' % h)
        self.__skip_hours = hours

    @property
    def skip_days(self):
        """Set of days in which podcatchers don't need to refresh this feed.

        The days are represented using strings of their dayname, like "Monday"
        or "wednesday".

        For example, to skip the weekend::

            >>> from feedgen import Podcast
            >>> p = Podcast()
            >>> p.skip_days = {"Friday", "Saturday", "sunday"}
            >>> p.skip_days
            {"Saturday", "Friday", "Sunday"}

        """
        return self.__skip_days

    @skip_days.setter
    def skip_days(self, days):
        if days is not None:
            if not isinstance(days, set):
                days = set(days)
            for d in days:
                if not d.lower() in ['monday', 'tuesday', 'wednesday', 'thursday',
                        'friday', 'saturday', 'sunday']:
                    raise ValueError('Invalid day %s' % d)
            self.__skip_days = {day.capitalize() for day in days}
        else:
            self.__skip_days = None

    @property
    def web_master(self):
        """The :class:`~feedgen.Person` responsible for
        technical issues relating to the feed.
        """
        return self.__web_master

    @web_master.setter
    def web_master(self, web_master):
        if web_master is not None:
            if (not hasattr(web_master, "email")) or not web_master.email:
                raise ValueError("The webmaster must have an email attribute "
                                 "and it must be set and not empty.")
        self.__web_master = web_master

    @property
    def category(self):
        """The iTunes category, which appears in the category column
        and in iTunes Store Browser.

        Use the :class:`feedgen.Category` class.
        """
        return self.__category

    @category.setter
    def category(self, category):
        if category is not None:
            # Check that the category quacks like a duck
            if hasattr(category, "category") and \
                    hasattr(category, "subcategory"):
                self.__category = category
            else:
                raise TypeError("A Category(-like) object must be used, got "
                                "%s" % category)
        else:
            self.__category = None

    @property
    def image(self):
        """The image for the podcast. This tag specifies the artwork
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
        requests for iTunes to be able to automatically update your cover art.
        """
        return self.__image

    @image.setter
    def image(self, image):
        if image is not None:
            lowercase_itunes_image = image.lower()
            if not (lowercase_itunes_image.endswith(('.jpg', '.jpeg', '.png'))):
                raise ValueError('Image filename must end with png or jpg, not '
                                 '.%s' % image.split(".")[-1])
            self.__image = image
        else:
            self.__image = None

    @property
    def complete(self):
        """Whether this podcast is completed or not.

        If you set this to ``True``, you are indicating that no more
        episodes will be added to the podcast. If you let this be ``None`` or
        ``False``, you are indicating that new episodes may be posted.

        .. warning::

            Setting this to ``True`` is the same as promising you'll never ever
            release a new episode. Do NOT set this to ``True`` as long as
            there's any chance at all that a new episode will be released
            someday.

        """
        return self.__complete

    @complete.setter
    def complete(self, complete):
        if complete is not None:
            self.__complete = bool(complete)
        else:
            self.__complete = None

    @property
    def owner(self):
        """The :class:`~feedgen.Person` who owns this podcast. iTunes
        will use this information to contact the owner of the podcast for
        communication specifically about the podcast. It will not be publicly
        displayed, but it will be in the feed source.

        Both the name and email are required.
        """
        return self.__owner

    @owner.setter
    def owner(self, owner):
        if owner is not None:
            if owner.name and owner.email:
                self.__owner = owner
            else:
                raise ValueError('Both name and email must be set.')
        else:
            self.__owner = None

    @property
    def feed_url(self):
        """The URL which this feed is available at.

        Identifying a feed's URL within the feed makes it more portable,
        self-contained, and easier to cache. You should therefore set this
        attribute if you're able to.
        """
        return self.__feed_url

    @feed_url.setter
    def feed_url(self, feed_url):
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

