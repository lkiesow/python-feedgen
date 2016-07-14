# -*- coding: utf-8 -*-
"""
    podgen.feed
    ~~~~~~~~~~~~

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de> and 2016, Thorben Dahl
        <thorben@sjostrom.no>

    :license: FreeBSD and LGPL, see license.* for more details.

"""
from future.utils import iteritems
from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from podgen.episode import Episode
from podgen.util import ensure_format, formatRFC2822, listToHumanreadableStr, \
    htmlencode
from podgen.person import Person
import podgen.version
import sys
from podgen.compat import string_types
import collections
import inspect
import warnings


_feedgen_version = podgen.version.version_str


class Podcast(object):
    """Class representing one podcast feed.

    The following attributes are mandatory:

    * :attr:`~podgen.Podcast.name`
    * :attr:`~podgen.Podcast.website`
    * :attr:`~podgen.Podcast.description`
    * :attr:`~podgen.Podcast.explicit`

    All attributes can be assigned :obj:`None` in addition to the types
    specified below. Types etc. are checked during assignment, to help you
    discover errors earlier. Duck typing is employed wherever a class in podgen
    is expected.

    There is a **shortcut** you can use when creating new Podcast objects, that
    lets you populate the attributes using the constructor. Use keyword
    arguments with the **attribute name as keyword** and the desired value as
    value. As an example::

        >>> import podgen
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

        self._nsmap = {
            'atom':  'http://www.w3.org/2005/Atom',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        """A dictionary which maps namespace prefixes to their namespace URI.
        Add a new entry here if you want to use that namespace.
        """

        ## RSS
        # http://www.rssboard.org/rss-specification
        # Mandatory:
        self.name = None
        """The name of the podcast as a :obj:`str`. It should be a human
        readable title. Often the same as the title of the associated website.
        This is mandatory and must not be blank.

        :type: :obj:`str`
        :RSS: title
        """

        self.website = None
        """The absolute URL of this podcast's website.

        This is one of the mandatory attributes.

        :type: :obj:`str`
        :RSS: link
        """

        self.description = None
        """The description of the podcast, which is a phrase or sentence
        describing it to potential new subscribers. It is mandatory for RSS
        feeds, and is shown under the podcast's name on the iTunes store page.

        :type: :obj:`str`
        :RSS: description
        """

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
        "clean" graphic will appear.

        :type: :obj:`bool`
        :RSS: itunes:explicit
        """

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
        notice.

        :type: :obj:`str`
        :RSS: copyright"""

        self.__docs = 'http://www.rssboard.org/rss-specification'

        self.generator = self._feedgen_generator_str
        """A string identifying the software that generated this RSS feed.
        Defaults to a string identifying PodGen.

        :type: :obj:`str`
        :RSS: generator

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
        http://www.loc.gov/standards/iso639-2/php/code_list.php

        :type: :obj:`str`
        :RSS: language
        """

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

        If you don't intend to submit this podcast to iTunes, you can set
        this to ``True`` as a way of giving iTunes the middle finger, and
        perhaps more importantly, preventing others from submitting it as well.

        Set it to ``True`` to withhold the entire podcast from iTunes. It is set
        to ``False`` by default, of course.

        :type: :obj:`bool`
        :RSS: itunes:block
        """

        self.__category = None

        self.__image = None

        self.__complete = None

        self.new_feed_url = None
        """When set, tell iTunes that your feed has moved to this URL.

        After adding this attribute, you should maintain the old feed
        for 48 hours before retiring it. At that point, iTunes will have updated
        the directory with the new feed URL.

        :type: :obj:`str`
        :RSS: itunes:new-feed-url

        .. warning::

            iTunes supports this mechanic of changing your feed's location.
            However, you cannot assume the same of everyone else who has
            subscribed to this podcast. Therefore, you should NEVER stop
            supporting an old location for your podcast. Instead, you should
            create HTTP redirects so those with the old address are redirected
            to your new address, and keep those redirects up for all eternity.

        .. warning::

            Make sure the new URL you set is correct, or else you're making
            people switch to a URL that doesn't work!
        """

        self.__owner = None

        self.subtitle = None
        """The subtitle for your podcast, shown mainly as a very short
        description on iTunes. The subtitle displays best if it is only a few
        words long, like a short slogan.

        :type: :obj:`str`
        :RSS: itunes:subtitle
        """

        self.pubsubhubbub = None
        """The URL at which the PubSubHubbub_ hub can be found.

        Podcatchers can tell the hub that they want to be notified when a new
        episode is released. This way, they don't need to check for new episodes
        every few hours; instead, the episodes arrive at their doorstep as soon
        as they're published, through a notification sent by the hub.

        :type: :obj:`str`
        :RSS: atom:link with ``rel="hub"``

        .. warning::

           Do NOT set this attribute if you haven't set up mechanics for
           notifying the hub of new episodes. Doing so could make it appear to
           your listeners like there is no new content for this feed. See the
           guide.

        .. seealso::
           The :doc:`guide on how to use PubSubHubbub </advanced/pubsubhubbub>`
              A step-for-step guide with examples.

        .. _PubSubHubbub: https://en.wikipedia.org/wiki/PubSubHubbub
        """

        self.xslt = None
        """
        Absolute URL to the XSLT file which web browsers should use with this
        feed.

        `XSLT`_ stands for Extensible Stylesheet Language Transformations and
        can be regarded as a template language made for transforming XML into
        XHTML (among other things). You can use it to avoid giving users an
        ugly XML listing when trying to subscribe to your podcast; this
        technique is in fact employed by most podcast publishers today.
        In a web browser, it looks like a web page, and to the
        podcatchers, it looks like a normal podcast feed. To put it another
        way, the very same URL can be used as an information web page about the
        podcast as well as the URL you subscribe to in podcatchers.

        :type: :obj:`str`
        :RSS: Processor instruction right after the xml declaration called
            ``xml-stylesheet``, with type set to ``text/xsl`` and href set to
            this attribute.

        .. note::

           Firefox will use its own stylesheet for RSS feeds, so you
           must test using another browser and possibly a `simple web server`_
           (``python -m http.server 8000 -b 127.0.0.1``).

        .. _XSLT: https://en.wikipedia.org/wiki/XSLT
        .. _simple web server:
           https://docs.python.org/3/library/http.server.html
        """

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
        """List of :class:`.Episode` objects that are part of this podcast.

        See :py:meth:`.add_episode` for an easy way to create new episodes and
        assign them to this podcast in one call.

        :type: :obj:`list` of :class:`podgen.Episode`
        :RSS: item elements
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
        objects, and you, too, may use it when creating episodes.

        By default, this property points to :py:class:`.Episode`.

        When assigning a new class to ``episode_class``, you must make sure that
        the new value (1) is a class and not an instance, and (2) that it is a
        subclass of Episode (or is Episode itself).

        Example of use::

            >>> # Create new podcast
            >>> from podgen import Podcast, Episode
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

        :type: :obj:`class` which extends :class:`podgen.Episode`
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

        :param new_episode: :class:`.Episode` object to add. A new instance of
            :attr:`.episode_class` is used if ``new_episode`` is omitted.
        :returns: Episode object created or passed to this function.

        Example::

            ...
            >>> episode1 = p.add_episode()
            >>> episode1.title = 'First episode'
            >>> # You may also provide an episode object yourself:
            >>> another_episode = p.add_episode(podgen.Episode())
            >>> another_episode.title = 'My second episode'

        Internally, this method creates a new instance of
        :attr:`~podgen.Episode.episode_class`, which means you can change what
        type of objects are created by changing
        :attr:`~podgen.Episode.episode_class`.

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
        ITUNES_NS = self._nsmap['itunes']

        feed = etree.Element('rss', version='2.0', nsmap=self._nsmap)
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
                                              '{%s}creator' % self._nsmap['dc'])
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
            # Ensure any modifications to the set are accounted for
            self.skip_hours = self.skip_hours
            skipHours = etree.SubElement(channel, 'skipHours')
            for h in self.skip_hours:
                hour = etree.SubElement(skipHours, 'hour')
                hour.text = str(h)
        if self.skip_days:
            # Ensure any modifications to the set are accounted for
            self.skip_days = self.skip_days
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
            link_to_self = etree.SubElement(channel, '{%s}link' % self._nsmap['atom'])
            link_to_self.attrib['href'] = self.feed_url
            link_to_self.attrib['rel'] = 'self'
            link_to_self.attrib['type'] = 'application/rss+xml'

        if self.pubsubhubbub:
            link_to_hub = etree.SubElement(channel, '{%s}link' % self._nsmap['atom'])
            link_to_hub.attrib['href'] = self.pubsubhubbub
            link_to_hub.attrib['rel'] = 'hub'

        for entry in self.episodes:
            item = entry.rss_entry()
            channel.append(item)

        return feed

    def _add_xslt_pi(self, rss, xml_declaration):
        """Add an XSLT processor instruction to the RSS string provided."""
        # This is a hackish way of getting a processor instruction between
        # the XML declaration and the RSS element; simply because lxml doesn't
        # support processor instructions outside the root element. So we do
        # a str.replace to replace the first newline with the processor
        # instruction, since the XML declaration is followed by a newline.

        # Get the processor instruction as a string
        pi = self._get_xslt_pi()
        if xml_declaration:
            return rss.replace(
             "\n",
             '\n%s\n' % pi,
             1)
        else:
            # No declaration, so just put it at the beginning (assuming the
            # caller wants it there, why else would you set self.xslt?)
            return pi + "\n" + rss

    def _get_xslt_pi(self):
        htmlescaped_url = htmlencode(self.xslt)
        quote_sanitized = htmlescaped_url.replace('"', '').replace("\\", "")
        return etree.tostring(etree.ProcessingInstruction(
            "xml-stylesheet",
            'type="text/xsl" href="' + quote_sanitized + '"',
        ), encoding="UTF-8").decode("UTF-8")

    def __str__(self):
        """Print the podcast in RSS format, using the default options.

        This method just calls :py:meth:`.rss_str` without arguments.
        """
        return self.rss_str()

    def rss_str(self, minimize=False, encoding='UTF-8',
                xml_declaration=True):
        """Generate an RSS feed and return the feed XML as string.

        :param minimize: Set to True to disable splitting the feed into multiple
            lines and adding properly indentation, saving bytes at the cost of
            readability (default: False).
        :type minimize: bool
        :param encoding: Encoding used in the XML declaration (default: UTF-8).
        :type encoding: str
        :param xml_declaration: Whether an XML declaration should be added to
            the output (default: True).
        :type xml_declaration: bool
        :returns: The generated RSS feed as a :obj:`str` (unicode in 2.7)
        """
        feed = self._create_rss()
        rss = etree.tostring(feed, pretty_print=not minimize, encoding=encoding,
                              xml_declaration=xml_declaration).decode(encoding)
        if self.xslt:
            return self._add_xslt_pi(rss, xml_declaration=xml_declaration)
        else:
            return rss

    def rss_file(self, filename, minimize=False,
                 encoding='UTF-8', xml_declaration=True):
        """Generate an RSS feed and write the resulting XML to a file.

        .. note::

           If atomicity is needed, then you are expected to provide that
           yourself. That means that you should write the feed to a temporary
           file which you rename to the final name afterwards; renaming is an
           atomic operation on Unix(like) systems.

        .. note::

           File-like objects given to this method will not be closed.

        :param filename: Name of file to write, or a file-like object, or a URL.
        :type filename: str or fd
        :param minimize: Set to True to disable splitting the feed into multiple
            lines and adding properly indentation, saving bytes at the cost of
            readability (default: False).
        :type minimize: bool
        :param encoding: Encoding used in the XML file (default: UTF-8).
        :type encoding: str
        :param xml_declaration: Whether an XML declaration should be added to
            the output (default: True).
        :type xml_declaration: bool
        :returns: Nothing.
        """
        rss = self.rss_str(minimize=minimize, encoding=encoding,
                           xml_declaration=xml_declaration)
        # Have we got a filename, or a file-like object?
        if isinstance(filename, string_types):
            # It is a string, assume it is filename
            with open(filename, "w") as fd:
                fd.write(rss)
        elif hasattr(filename, "write"):
            # It is file-like enough to fool us
            filename.write(rss)
        else:
            raise TypeError("filename must either be a filename (str/unicode) "
                            "or a file-like object (with write method); "
                            "%s satisfies none of those conditions." % filename)

    def apply_episode_order(self):
        """Make sure that the episodes appear on iTunes in the exact order
        they have in :attr:`~.Podcast.episodes`.

        This will set each :attr:`.Episode.position` so it matches the episode's
        position in :attr:`.Podcast.episodes`.

        If you're using some :class:`.Episode` objects in multiple podcast
        feeds and you don't use this method with every feed, you might want to
        call :meth:`.Podcast.clear_episode_order` after generating this feed's
        RSS so an episode's position in this feed won't affect its position in
        the other feeds.
        """
        for i, episode in enumerate(self.episodes):
            position = i + 1
            episode.position = position

    def clear_episode_order(self):
        """Reset :attr:`.Episode.position` for every single episode.

        Use this if you want to reuse an :class:`.Episode` object in another
        feed, and don't want its position in this feed to affect where it
        appears in the other feed. This is not needed if you'll call
        :meth:`.Podcast.apply_episode_order` on the other feed, though."""
        for episode in self.episodes:
            episode.position = None

    @property
    def last_updated(self):
        """The last time the feed was generated. It defaults to the time and
        date at which the RSS is generated, if set to :obj:`None`. The default
        should be sufficient for most, if not all, use cases.

        The value can either be a string, which will automatically be parsed
        into a :class:`datetime.datetime` object when assigned, or a
        :class:`datetime.datetime` object. In any case, the time and date must
        be timezone aware.

        Set this to ``False`` to leave out this element instead of using the
        default.

        :type: :class:`datetime.datetime`, :obj:`str` (will be converted to
           and stored as :class:`datetime.datetime`), :obj:`None` for default or
           :obj:`False` to leave out.
        :RSS: lastBuildDate
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
        that supports the (somewhat dated) rssCloud interface, which can be
        implemented in HTTP-POST, XML-RPC or SOAP 1.1.

        The tuple should look like this: ``(domain, port, path,
        registerProcedure, protocol)``.

        :domain: The domain where the webservice can be found.
        :port: The port the webservice listens to.
        :path: The path of the webservice.
        :registerProcedure: The procedure to call.
        :protocol: Can be either "HTTP-POST", "xml-rpc" or "soap".

        Example::

            p.cloud = ("podcast.example.org", 80, "/rpc", "cloud.notify",
                       "xml-rpc")

        :type: :obj:`tuple` with (:obj:`str`, :obj:`int`, :obj:`str`,
           :obj:`str`, :obj:`str`)
        :RSS: cloud

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
                      exclude_podgen=False):
        """Set the generator of the feed, formatted nicely, which identifies the
        software used to generate the feed.

        :param generator: Software used to create the feed.
        :type generator: str
        :param version: (Optional) Version of the software, as a tuple.
        :type version: :obj:`tuple` of :obj:`int`
        :param uri: (Optional) The software's website.
        :type uri: str
        :param exclude_podgen: (Optional) Set to True if you don't want
            PodGen to be mentioned (e.g., "My Program (using PodGen 1.0.0)")
        :type exclude_podgen: bool

        .. seealso::

           The attribute :py:attr:`.generator`
              Lets you access and set the generator string yourself, without
              any formatting help.
        """
        self.generator = self._program_name_to_str(generator, version, uri) + \
                         (" (using %s)" % self._feedgen_generator_str
                                if not exclude_podgen else "")

    def _program_name_to_str(self, generator=None, version=None, uri=None):
        return generator + \
                ((" v" + ".".join([str(i) for i in version])) if version is not None else "") + \
                ((" " + uri) if uri else "")

    @property
    def _feedgen_generator_str(self):
        return self._program_name_to_str(
                                       podgen.version.name,
                                       podgen.version.version_full,
                                       podgen.version.website
                                   )


    @property
    def authors(self):
        """List of :class:`~podgen.Person` that are responsible for this
        podcast's editorial content.

        Any value you assign to authors will be automatically converted to a
        list, but only if it's iterable (like tuple, set and so on). It is an
        error to assign a single :class:`~podgen.person.Person` object to this
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

        :type: :obj:`list` of :class:`podgen.Person`
        :RSS: managingEditor or dc:creator, and itunes:author
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
        """The publication date for the content in this podcast. You
        probably want to use the default value.

        :Default value: If this is :obj:`None` when the feed is generated, the
           publication date of the episode with the latest publication date
           (which may be in the future) is used. If there are no episodes, the
           publication date is omitted from the feed.

        If you set this to a :obj:`str`, it will be parsed and made into a
        :class:`datetime.datetime` object when assigned. You may also set it to
        a :class:`datetime.datetime` object directly. In any case, the time and
        date must be timezone aware.

        If you want to forcefully omit the publication date from the feed, set
        this to ``False``.

        :type: :class:`datetime.datetime`, :obj:`str` (will be converted to
           and stored as :class:`datetime.datetime`), :obj:`None` for default or
           :obj:`False` to leave out.
        :RSS: pubDate
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
        """Set of hours of the day in which podcatchers don't need to refresh
        this feed.

        This isn't widely supported by podcatchers.

        The hours are represented as integer values from 0 to 23.
        Note that while the content of the set is checked when it is first
        assigned to ``skip_hours``, further changes to the set "in place" will
        not be checked before you generate the RSS.

        For example, to stop refreshing the feed between 18 and 7::

            >>> from podgen import Podcast
            >>> p = Podcast()
            >>> p.skip_hours = set(range(18, 24))
            >>> p.skip_hours
            {18, 19, 20, 21, 22, 23}
            >>> p.skip_hours |= set(range(8))
            >>> p.skip_hours
            {0, 1, 2, 3, 4, 5, 6, 7, 18, 19, 20, 21, 22, 23}

        :type: :obj:`set` of :obj:`int`
        :RSS: skipHours
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

        This isn't widely supported by podcatchers.

        The days are represented using strings of their English names, like
        "Monday" or "wednesday". The day names are automatically capitalized
        when the set is assigned to ``skip_days``, but subsequent changes to the
        set "in place" are only checked and capitalized when the RSS feed is
        generated.

        For example, to stop refreshing the feed in the weekend::

            >>> from podgen import Podcast
            >>> p = Podcast()
            >>> p.skip_days = {"Friday", "Saturday", "sUnDaY"}
            >>> p.skip_days
            {"Saturday", "Friday", "Sunday"}

        :type: :obj:`set` of :obj:`str`
        :RSS: skipDays
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
            self.__skip_days = set(day.capitalize() for day in days)
        else:
            self.__skip_days = None

    @property
    def web_master(self):
        """The :class:`~podgen.Person` responsible for
        technical issues relating to the feed.

        :type: :class:`podgen.Person`
        :RSS: webMaster
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
        and in iTunes Store listings.

        :type: :class:`podgen.Category`
        :RSS: itunes:category
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
        """The URL of the artwork for this podcast. iTunes
        prefers square images that are at least ``1400x1400`` pixels.
        Podcasts with an image smaller than this are *not* eligible to be
        featured on the iTunes Store.

        iTunes supports images in JPEG and PNG formats with an RGB color space
        (CMYK is not supported). The URL must end in ".jpg" or ".png".

        :type: :obj:`str`
        :RSS: itunes:image

        .. note::

           If you change your podcast’s image, you must also change the file’s
           name; iTunes doesn't check the image to see if it has changed.

           Additionally, the server hosting your cover art image must allow HTTP
           HEAD requests (most servers support this).
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

        :type: :obj:`bool`
        :RSS: itunes:complete

        .. warning::

            Setting this to ``True`` is the same as promising you'll never ever
            release a new episode. Do NOT set this to ``True`` as long as
            there's any chance AT ALL that a new episode will be released
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
        """The :class:`~podgen.Person` who owns this podcast. iTunes
        will use this person's name and email address for all correspondence
        related to this podcast. It will not be publicly displayed, but it's
        still publicly available in the RSS source.

        Both the name and email are required.

        :type: :class:`podgen.Person`
        :RSS: itunes:owner
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

        :type: :obj:`str`
        :RSS: atom:link with ``rel="self"``
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

