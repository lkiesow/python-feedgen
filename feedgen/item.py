# -*- coding: utf-8 -*-
"""
    feedgen.entry
    ~~~~~~~~~~~~~

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
"""
import collections

from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from feedgen.util import ensure_format, formatRFC2822, htmlencode, \
    listToHumanreadableStr
from feedgen.compat import string_types
from builtins import str


class BaseEpisode(object):
    """Class representing an episode in a podcast. Corresponds to an RSS Item.

    Its name indicates that this is the superclass for all episode classes.
    It is not meant to indicate that this class misses functionality; in 99%
    of all cases, this class is the right one to use for episodes.
    """

    def __init__(self):
        # RSS
        self.__authors = []
        self.__summary = None
        self.__media = None
        self.__id = None
        self.__rss_link = None
        self.__publication_date = None
        self.__title = None

        # ITunes tags
        # http://www.apple.com/itunes/podcasts/specs.html#rss
        self.__withhold_from_itunes = None
        self.__image = None
        self.__itunes_duration = None
        self.__explicit = None
        self.__is_closed_captioned = None
        self.__position = None
        self.__subtitle = None

    def rss_entry(self):
        """Create a RSS item and return it."""

        ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        DUBLIN_NS = 'http://purl.org/dc/elements/1.1/'

        entry = etree.Element('item')

        if not (self.__title or self.__summary):
            raise ValueError('Required fields not set')

        if self.__title:
            title = etree.SubElement(entry, 'title')
            title.text = self.__title

        if self.__rss_link:
            link = etree.SubElement(entry, 'link')
            link.text = self.__rss_link

        if self.__summary:
            description = etree.SubElement(entry, 'description')
            description.text = etree.CDATA(self.__summary)
            content = etree.SubElement(entry, '{%s}encoded' %
                                    'http://purl.org/rss/1.0/modules/content/')
            content.text = etree.CDATA(self.__summary)

        if self.__authors:
            authors_with_name = [a.name for a in self.__authors if a.name]
            if authors_with_name:
                # We have something to display as itunes:author, combine all
                # names
                itunes_author = \
                    etree.SubElement(entry, '{%s}author' % ITUNES_NS)
                itunes_author.text = listToHumanreadableStr(authors_with_name)
            if len(self.__authors) > 1 or not self.__authors[0].email:
                # Use dc:creator, since it supports multiple authors (and
                # author without email)
                for a in self.__authors or []:
                    author = etree.SubElement(entry, '{%s}creator' % DUBLIN_NS)
                    if a.name and a.email:
                        author.text = "%s <%s>" % (a.name, a.email)
                    elif a.name:
                        author.text = a.name
                    else:
                        author.text = a.email
            else:
                # Only one author and with email, so use rss author
                author = etree.SubElement(entry, 'author')
                author.text = str(self.__authors[0])

        if self.__id:
            rss_guid = self.__id
        elif self.__media and self.__id is None:
            rss_guid = self.__media.url
        else:
            # self.__rss_guid was set to boolean False, or no enclosure
            rss_guid = None
        if rss_guid:
            guid = etree.SubElement(entry, 'guid')
            guid.text = rss_guid
            guid.attrib['isPermaLink'] = 'false'

        if self.__media:
            enclosure = etree.SubElement(entry, 'enclosure')
            enclosure.attrib['url'] = self.__media.url
            enclosure.attrib['length'] = str(self.__media.size)
            enclosure.attrib['type'] = self.__media.type

        if self.__publication_date:
            pubDate = etree.SubElement(entry, 'pubDate')
            pubDate.text = formatRFC2822(self.__publication_date)

        if not self.__withhold_from_itunes is None:
            block = etree.SubElement(entry, '{%s}block' % ITUNES_NS)
            block.text = 'yes' if self.__withhold_from_itunes else 'no'

        if self.__image:
            image = etree.SubElement(entry, '{%s}image' % ITUNES_NS)
            image.attrib['href'] = self.__image

        if self.__itunes_duration:
            duration = etree.SubElement(entry, '{%s}duration' % ITUNES_NS)
            duration.text = self.__itunes_duration

        if self.__explicit in ('yes', 'no', 'clean'):
            explicit = etree.SubElement(entry, '{%s}explicit' % ITUNES_NS)
            explicit.text = self.__explicit

        if not self.__is_closed_captioned is None:
            is_closed_captioned = etree.SubElement(entry, '{%s}isClosedCaptioned' % ITUNES_NS)
            is_closed_captioned.text = 'yes' if self.__is_closed_captioned else 'no'

        if not self.__position is None and self.__position >= 0:
            order = etree.SubElement(entry, '{%s}order' % ITUNES_NS)
            order.text = str(self.__position)

        if self.__subtitle:
            subtitle = etree.SubElement(entry, '{%s}subtitle' % ITUNES_NS)
            subtitle.text = self.__subtitle

        return entry

    def title(self, title=None):
        """Get or set this episode's human-readable title.
        Title is mandatory and should not be blank.

        :param title: This new title of this episode.
        :returns: This episode's title.
        """
        if not title is None:
            self.__title = title
        return self.__title

    def id(self, new_id=None):
        """Get or set this episode's globally unique identifier.

        If not present, the URL of the enclosed media is used. This is usually
        the best way to go, **as long as the media URL doesn't change**.

        Set the id to boolean False if you don't want to associate any id to
        this episode.

        It is important that an episode keeps the same ID until the end of time,
        since the ID is used by clients to identify which episodes have been
        listened to, which episodes are new, and so on. Changing the ID causes
        the same consequences as deleting the existing episode and adding a
        new, identical episode.

        Note that this is a GLOBALLY unique identifier. Thus, not only must it
        be unique in this podcast, it must not be the same ID as any other
        episode for any podcast out there. To ensure this, you should use a
        domain which you own (for example, use something like
        http://example.org/podcast/episode1 if you own example.org).

        This property corresponds to the RSS GUID element.

        :param new_id: Globally unique, permanent id of this episode.
        :returns: Id of this episode.
        """
        if not new_id is None:
            self.__id = new_id
        return self.__id

    @property
    def authors(self):
        """List of :class:`~feedgen.person.Person` that contributed to this
        episode.

        The authors don't need to have both name and email set. The names are
        shown under the podcast's title on iTunes.

        .. note::

            You do not need to provide any authors for an episode if
            they're identical to the podcast's authors.

        Any value you assign to authors will be automatically converted to a
        list, but only if it's iterable (like tuple, set and so on). It is an
        error to assign a single :class:`~feedgen.person.Person` object to this
        attribute::

            >>> # This results in an error
            >>> ep.authors = Person("John Doe", "johndoe@example.org")
            TypeError: Only iterable types can be assigned to authors, ...
            >>> # This is the correct way:
            >>> ep.authors = [Person("John Doe", "johndoe@example.org")]

        The initial value is an empty list, so you can use the list methods
        right away.

        Example::

            >>> # This attribute is just a list - you can for example append:
            >>> ep.authors.append(Person("John Doe", "johndoe@example.org"))
            >>> # Or assign a new list (discarding earlier authors)
            >>> ep.authors = [Person("John Doe", "johndoe@example.org"),
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

    def summary(self, new_summary=None, html=True):
        """Get or set the summary of this episode.

        In iTunes, the summary is shown in a separate window that appears when
        the "circled i" in the Description column is clicked. This field can be
        up to 4000 characters in length.

        See also :py:meth:`.BaseEpisode.itunes_subtitle`.

        :param new_summary: The summary of this episode.
        :param html: Treat the summary as HTML. If set to False, the summary
            will be HTML escaped (thus, any tags will be displayed in plain
            text). If set to True, the tags are parsed by clients which support
            HTML, but if something is not to be regarded as HTML, you must
            escape it yourself using HTML entities.
        :returns: Summary of this episode.
        """
        if not new_summary is None:
            if not html:
                new_summary = htmlencode(new_summary)
            self.__summary = new_summary
        return self.__summary

    def link(self, link=None):
        """Get or set the link to the full version of this episode description.

        :param link: the URI of the referenced resource (typically a Web page)
        :type link: str
        :returns: The current link URI.
        """
        if not link is None:
            self.__rss_link = link
        return self.__rss_link

    def publication_date(self, publication_date=None):
        """Set or get the time that this episode first was made public.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In both cases you must ensure that the value
        includes timezone information.

        :param publication_date: The date this episode was first made public.
        :type publication_date: datetime.datetime or str or None
        :returns: Creation date as datetime.datetime
        """
        if not publication_date is None:
            if isinstance(publication_date, string_types):
                publication_date = dateutil.parser.parse(publication_date)
            if not isinstance(publication_date, datetime):
                raise ValueError('Invalid datetime format')
            if publication_date.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__publication_date = publication_date

        return self.__publication_date

    def media(self, media=None):
        """Get or set the :class:`~feedgen.media.Media` object that is attached
        to this episode.

        Note that if :py:meth:`.id` is not set, the enclosure's url is used as
        the globally unique identifier. If you rely on this, you should make
        sure the url never changes, since changing the id messes up with clients
        (they will think this episode is new again, even if the user already
        has listened to it). Therefore, you should only rely on this behaviour
        if you own the domain which the episodes reside on. If you don't, then
        you must set :py:meth:`.id` to an appropriate value manually.

        :param media: The Media object which points to the media file you want
            to attach to this episode.
        :type media: feedgen.media.Media or None
        :returns: The media file attached to this episode.
        """
        if not media is None:
            # Test that the media quacks like a duck
            if hasattr(media, "url") and hasattr(media, "size") and \
               hasattr(media, "type"):
                # It's a duck
                self.__media = media
            else:
                raise TypeError("The parameter media must have the attributes "
                                "url, size and type.")
        return self.__media

    def withhold_from_itunes(self, withhold_from_itunes=None):
        """Get or set the ITunes block attribute. Use this to prevent episodes
        from appearing in the iTunes podcast directory. Note that the episode
        can still be found by inspecting the XML, so it is still public.

        One use case is if you know that this episode will get you kicked
        out from iTunes, should it make it there. In such cases, you can set
        withhold_from_itunes to ``True`` so this episode isn't published on
        iTunes, allowing you to publish it to everyone else while keeping your
        podcast on iTunes.

        This attribute defaults to ``False``, of course.

        :param withhold_from_itunes: Block podcast episode from iTunes.
        :type withhold_from_itunes: bool
        :returns: Whether the podcast episode is withheld from iTunes or not.
        """
        if not withhold_from_itunes is None:
            self.__withhold_from_itunes = withhold_from_itunes
        return self.__withhold_from_itunes

    def image(self, image=None):
        """Get or set the image for the podcast episode. This tag specifies the
        artwork for your podcast. Put the URL to the image in the href attribute.
        iTunes prefers square .jpg images that are at least 1400x1400 pixels,
        which is different from what is specified for the standard RSS image tag.
        In order for a podcast to be eligible for an iTunes Store feature, the
        accompanying image must be at least 1400x1400 pixels.

        iTunes supports images in JPEG and PNG formats with an RGB color space
        (CMYK is not supported). The URL must end in ".jpg" or ".png". If the
        <itunes:image> tag is not present, iTunes will use the contents of the
        RSS image tag.

        If you change your podcast’s image, also change the file’s name. iTunes
        may not change the image if it checks your feed and the image URL is the
        same. The server hosting your cover art image must allow HTTP head
        requests for iTS to be able to automatically update your cover art.
        
        Oh, and iTunes doesn't support this. You need to embed the image inside
        the media file as well (like regular album covers). The Podcast.image
        attribute is used if not.

        :param image: Image of the episode.
        :type image: str
        :returns: Image of the episode.
        """
        if not image is None:
            lowercase_image = image.lower()
            if not (lowercase_image.endswith(('.jpg', '.jpeg', '.png'))):
                raise ValueError('Image filename must end with png or jpg, not .%s' % image.split(".")[-1])
            self.__image = image
        return self.__image

    def itunes_duration(self, itunes_duration=None):
        """Get or set the duration of the podcast episode. The content of this
        tag is shown in the Time column in iTunes.

        The tag can be formatted HH:MM:SS, H:MM:SS, MM:SS, or M:SS (H = hours,
        M = minutes, S = seconds). If an integer is provided (no colon present),
        the value is assumed to be in seconds. If one colon is present, the
        number to the left is assumed to be minutes, and the number to the right
        is assumed to be seconds. If more than two colons are present, the
        numbers farthest to the right are ignored.

        :param itunes_duration: Duration of the podcast episode.
        :type itunes_duration: str or int
        :returns: Duration of the podcast episode.
        """
        if not itunes_duration is None:
            itunes_duration = str(itunes_duration)
            if len(itunes_duration.split(':')) > 3 or \
                            itunes_duration.lstrip('0123456789:') != '':
                ValueError('Invalid duration format "%s"' % itunes_duration)
            self.__itunes_duration = itunes_duration
        return self.itunes_duration

    def explicit(self, explicit=None):
        """Get or the the itunes:explicit value of the podcast episode. This tag
        should be used to indicate whether your podcast episode contains explicit
        material.
        
        The value of the podcast's explicit attribute is used by default.

        If you set this to ``True``, an "explicit" parental advisory
        graphic will appear in the Name column in iTunes. If the value is 
        ``False``, the parental advisory type is considered Clean, meaning that 
        no explicit language or adult content is included anywhere in this 
        episode, and a "clean" graphic will appear.
        
        :param explicit: ``True`` if the podcast contains material 
            that may be inappropriate for children, ``False`` if it doesn't.
        :type explicit: str
        :returns: If the podcast episode contains explicit material.
        """
        if not explicit is None:
            if not explicit in ('', 'yes', 'no', 'clean'):
                raise ValueError('Invalid value "%s" for explicit tag' % explicit)
            self.__explicit = explicit
        return self.__explicit

    def is_closed_captioned(self, is_closed_captioned=None):
        """Get or set the is_closed_captioned value of the podcast episode. This
        tag should be used if your podcast includes a video episode with 
        embedded closed captioning support. The two values for this tag are 
        ``True`` and ``False``.

        :param is_closed_captioned: If the episode has closed captioning 
            support.
        :type is_closed_captioned: bool or None
        :returns: If the episode has closed captioning support.
        """
        if not is_closed_captioned is None:
            self.__is_closed_captioned = is_closed_captioned
        return self.__is_closed_captioned

    def position(self, position=None):
        """Get or set the itunes:order value of this podcast episode. This tag 
        can be used to override the default ordering of episodes on the store.

        This tag is used at an <item> level by populating with the number value
        in which you would like the episode to appear on the store. For example,
        if you would like an <item> to appear as the first episode in the
        podcast, you would populate the <itunes:order> tag with “1”. If
        multiple episodes share the same position, they will be sorted by their
        publication date.

        To remove the order from the episode set the position to a value below 
        zero.

        :param position: This episode's desired position on the iTunes store
            page.
        :type position: int
        :returns: This episode's desired position on the iTunes Store page.
        """
        if not position is None:
            self.__position = int(position)
        return self.__position

    def subtitle(self, subtitle=None):
        """Get or set the itunes:subtitle value for the podcast episode. The
        contents of this tag are shown in the Description column in iTunes. The
        subtitle displays best if it is only a few words long.

        :param subtitle: Subtitle of the podcast episode.
        :type subtitle: str
        :returns: Subtitle of the podcast episode.
        """
        if not subtitle is None:
            self.__subtitle = subtitle
        return self.__subtitle
