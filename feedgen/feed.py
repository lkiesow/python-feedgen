# -*- coding: utf-8 -*-
'''
    feedgen.feed
    ~~~~~~~~~~~~

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.

'''

from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from feedgen.entry import FeedEntry
from feedgen.util import ensure_format, formatRFC2822
import feedgen.version
import sys
from feedgen.compat import string_types
import collections


_feedgen_version = feedgen.version.version_str


class FeedGenerator(object):
    '''FeedGenerator for generating RSS feeds.
    '''


    def __init__(self):
        self.__extensions = {}
        self.__feed_entries = []

        ## RSS
        # http://www.rssboard.org/rss-specification
        self.__rss_title       = None
        self.__rss_link        = None
        self.__rss_description = None

        self.__rss_author = None
        self.__rss_category       = None
        self.__rss_cloud          = None
        self.__rss_copyright      = None
        self.__rss_docs           = 'http://www.rssboard.org/rss-specification'
        self.__rss_generator      = 'python-feedgen'
        self.__rss_image          = None
        self.__rss_language       = None
        self.__rss_lastBuildDate  = datetime.now(dateutil.tz.tzutc())
        self.__rss_managingEditor = None
        self.__rss_pubDate        = None
        self.__rss_rating         = None
        self.__rss_skipHours      = None
        self.__rss_skipDays       = None
        self.__rss_textInput      = None
        self.__rss_ttl            = None
        self.__rss_webMaster      = None

        ## ITunes tags
        # http://www.apple.com/itunes/podcasts/specs.html#rss
        self.__itunes_author = None
        self.__itunes_block = None
        self.__itunes_category = None
        self.__itunes_image = None
        self.__itunes_explicit = None
        self.__itunes_complete = None
        self.__itunes_new_feed_url = None
        self.__itunes_owner = None
        self.__itunes_subtitle = None
        self.__itunes_summary = None



    def _create_rss(self, extensions=True):
        '''Create an RSS feed xml structure containing all previously set fields.

        :returns: Tuple containing the feed root element and the element tree.
        '''

        nsmap = {
            'atom':  'http://www.w3.org/2005/Atom',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
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
        if self.__rss_category:
            for cat in self.__rss_category:
                category = etree.SubElement(channel, 'category')
                category.text = cat['value']
                if cat.get('domain'):
                    category.attrib['domain'] = cat['domain']
        if self.__rss_cloud:
            cloud = etree.SubElement(channel, 'cloud')
            cloud.attrib['domain'] = self.__rss_cloud.get('domain')
            cloud.attrib['port'] = self.__rss_cloud.get('port')
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
        if self.__rss_image:
            image = etree.SubElement(channel, 'image')
            url = etree.SubElement(image, 'url')
            url.text = self.__rss_image.get('url')
            title = etree.SubElement(image, 'title')
            title.text = self.__rss_image['title'] \
                    if self.__rss_image.get('title') else self.__rss_title
            link = etree.SubElement(image, 'link')
            link.text = self.__rss_image['link'] \
                    if self.__rss_image.get('link') else self.__rss_link
            if self.__rss_image.get('width'):
                width = etree.SubElement(image, 'width')
                width.text = self.__rss_image.get('width')
            if self.__rss_image.get('height'):
                height = etree.SubElement(image, 'height')
                height.text = self.__rss_image.get('height')
            if self.__rss_image.get('description'):
                description = etree.SubElement(image, 'description')
                description.text = self.__rss_image.get('description')
        if self.__rss_language:
            language = etree.SubElement(channel, 'language')
            language.text = self.__rss_language
        if self.__rss_lastBuildDate:
            lastBuildDate = etree.SubElement(channel, 'lastBuildDate')

            lastBuildDate.text = formatRFC2822(self.__rss_lastBuildDate)
        if self.__rss_managingEditor:
            managingEditor = etree.SubElement(channel, 'managingEditor')
            managingEditor.text = self.__rss_managingEditor
        if self.__rss_pubDate:
            pubDate = etree.SubElement(channel, 'pubDate')
            pubDate.text = formatRFC2822(self.__rss_pubDate)
        if self.__rss_rating:
            rating = etree.SubElement(channel, 'rating')
            rating.text = self.__rss_rating
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
        if self.__rss_textInput:
            textInput = etree.SubElement(channel, 'textInput')
            textInput.attrib['title'] = self.__rss_textInput.get('title')
            textInput.attrib['description'] = self.__rss_textInput.get('description')
            textInput.attrib['name'] = self.__rss_textInput.get('name')
            textInput.attrib['link'] = self.__rss_textInput.get('link')
        if self.__rss_ttl:
            ttl = etree.SubElement(channel, 'ttl')
            ttl.text = str(self.__rss_ttl)
        if self.__rss_webMaster:
            webMaster = etree.SubElement(channel, 'webMaster')
            webMaster.text = self.__rss_webMaster

        if self.__itunes_author:
            author = etree.SubElement(channel, '{%s}author' % ITUNES_NS)
            author.text = self.__itunes_author

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
            owner_name.text = self.__itunes_owner.get('name')
            owner_email = etree.SubElement(owner, '{%s}email' % ITUNES_NS)
            owner_email.text = self.__itunes_owner.get('email')

        if self.__itunes_subtitle:
            subtitle = etree.SubElement(channel, '{%s}subtitle' % ITUNES_NS)
            subtitle.text = self.__itunes_subtitle

        if self.__itunes_summary:
            summary = etree.SubElement(channel, '{%s}summary' % ITUNES_NS)
            summary.text = self.__itunes_summary

        if extensions:
            for ext in self.__extensions.values() or []:
                if ext.get('rss'):
                    ext['inst'].extend_rss(feed)

        for entry in self.__feed_entries:
            item = entry.rss_entry()
            channel.append(item)

        doc = etree.ElementTree(feed)
        return feed, doc


    def rss_str(self, pretty=False, extensions=True, encoding='UTF-8',
            xml_declaration=True):
        '''Generates an RSS feed and returns the feed XML as string.

        :param pretty: If the feed should be split into multiple lines and
            properly indented.
        :type pretty: bool
        :param extensions: Enable or disable the loaded extensions for the xml
            generation (default: enabled).
        :type extensions: bool
        :param encoding: Encoding used in the  XML file (default: UTF-8).
        :type encoding: str
        :param xml_declaration: If an XML declaration should be added to the
            output (Default: enabled).
        :type xml_declaration: bool
        :returns: String representation of the RSS feed.
        '''
        feed, doc = self._create_rss(extensions=extensions)
        return etree.tostring(feed, pretty_print=pretty, encoding=encoding,
                xml_declaration=xml_declaration)


    def rss_file(self, filename, extensions=True, pretty=False,
            encoding='UTF-8', xml_declaration=True):
        '''Generates an RSS feed and write the resulting XML to a file.

        :param filename: Name of file to write, or a file-like object, or a URL.
        :type filename: str or fd
        :param extensions: Enable or disable the loaded extensions for the xml
            generation (default: enabled).
        :type extensions: bool
        :param pretty: If the feed should be split into multiple lines and
            properly indented.
        :type pretty: bool
        :param encoding: Encoding used in the  XML file (default: UTF-8).
        :type encoding: str
        :param xml_declaration: If an XML declaration should be added to the
            output (Default: enabled).
        :type xml_declaration: bool
        '''
        feed, doc = self._create_rss(extensions=extensions)
        doc.write(filename, pretty_print=pretty, encoding=encoding,
                xml_declaration=xml_declaration)


    def title(self, title=None):
        '''Get or set the title value of the feed. It should contain a human
        readable title for the feed. Often the same as the title of the
        associated website. Title is mandatory for both ATOM and RSS and should
        not be blank.

        :param title: The new title of the feed.
        :type title: str
        :returns: The feeds title.
        '''
        if not title is None:
            self.__rss_title = title
        return self.__rss_title


    def updated(self, updated=None):
        '''Set or get the updated value which indicates the last time the feed
        was modified in a significant way.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        This will set both atom:updated and rss:lastBuildDate.

        Default value
            If not set, updated has as value the current date and time.

        :param updated: The modification date.
        :type updated: str or datetime.datetime
        :returns: Modification date as datetime.datetime
        '''
        # TODO: Standardize on one way to set publication date
        if not updated is None:
            if isinstance(updated, string_types):
                updated = dateutil.parser.parse(updated)
            if not isinstance(updated, datetime):
                raise ValueError('Invalid datetime format')
            if updated.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__rss_lastBuildDate = updated

        return self.__rss_lastBuildDate


    def lastBuildDate(self, lastBuildDate=None):
        '''Set or get the lastBuildDate value which indicates the last time the
        content of the channel changed.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        This will set both atom:updated and rss:lastBuildDate.

        Default value
            If not set, lastBuildDate has as value the current date and time.

        :param lastBuildDate: The modification date.
        :type updated: str or datetime.datetime
        :returns: Modification date as datetime.datetime
        '''
        return self.updated( lastBuildDate )


    def author(self, author=None, replace=False, **kwargs):
        '''Get or set author data. An author element is a dictionary containing a name,
        an email address and a URI. Name is mandatory for ATOM, email is mandatory
        for RSS.

        This method can be called with:

        - the fields of an author as keyword arguments
        - the fields of an author as a dictionary
        - a list of dictionaries containing the author fields

        An author has the following fields:

        - *name* conveys a human-readable name for the person.
        - *uri* contains a home page for the person.
        - *email* contains an email address for the person.

        :param author:  Dictionary or list of dictionaries with author data.
        :param replace: Add or replace old data.
        :returns: List of authors as dictionaries.

        Example::

            >>> feedgen.author( { 'name':'John Doe', 'email':'jdoe@example.com' } )
            [{'name':'John Doe','email':'jdoe@example.com'}]

            >>> feedgen.author([{'name':'Mr. X'},{'name':'Max'}])
            [{'name':'John Doe','email':'jdoe@example.com'},
                    {'name':'John Doe'}, {'name':'Max'}]

            >>> feedgen.author( name='John Doe', email='jdoe@example.com', replace=True )
            [{'name':'John Doe','email':'jdoe@example.com'}]

        '''
        if author is None and kwargs:
            author = kwargs
        if not author is None:
            if replace or self.__rss_author is None:
                self.__rss_author = []
            self.__rss_author += ensure_format( author,
                    set(['name', 'email']), set(['name', 'email']))
        return self.__rss_author


    def link(self, href=None):
        '''Get or set the feed's link (website).

        :param href:    URI of this feed's website.

        Example::

            >>> feedgen.link( href='http://example.com/')
            [{'href':'http://example.com/', 'rel':'self'}]

        '''
        if not href is None:
            self.__rss_link = href
        return self.__rss_link


    def category(self, category=None, replace=False, **kwargs):
        '''Get or set categories that the feed belongs to.

        This method can be called with:

        - the fields of a category as keyword arguments
        - the fields of a category as a dictionary
        - a list of dictionaries containing the category fields

        A categories has the following fields:

        - *term* identifies the category
        - *scheme* identifies the categorization scheme via a URI.

        If a label is present it is used for the RSS feeds. Otherwise the term is
        used. The scheme is used for the domain attribute in RSS.

        :param category:    Dict or list of dicts with data.
        :param replace: Add or replace old data.
        :returns: List of category data.
        '''
        if category is None and kwargs:
            category = kwargs
        if not category is None:
            if replace or self.__rss_category is None:
                self.__rss_category = []
            if isinstance(category, collections.Mapping):
                category = [category]
            for cat in category:
                rss_cat = dict()
                rss_cat['value'] = cat['label'] if cat.get('label') else cat['term']
                if cat.get('scheme'):
                    rss_cat['domain'] = cat['scheme']
                self.__rss_category.append( rss_cat )
        return self.__rss_category


    def cloud(self, domain=None, port=None, path=None, registerProcedure=None,
            protocol=None):
        '''Set or get the cloud data of the feed. It is an RSS only attribute. It
        specifies a web service that supports the rssCloud interface which can be
        implemented in HTTP-POST, XML-RPC or SOAP 1.1.

        :param domain: The domain where the webservice can be found.
        :param port: The port the webservice listens to.
        :param path: The path of the webservice.
        :param registerProcedure: The procedure to call.
        :param protocol: Can be either HTTP-POST, XML-RPC or SOAP 1.1.
        :returns: Dictionary containing the cloud data.
        '''
        if not domain is None:
            self.__rss_cloud = {'domain':domain, 'port':port, 'path':path,
                    'registerProcedure':registerProcedure, 'protocol':protocol}
        return self.__rss_cloud


    def generator(self, generator=None, version=None, uri=None):
        '''Get or the generator of the feed which identifies the software used to
        generate the feed, for debugging and other purposes.

        :param generator: Software used to create the feed.
        :param version: (Optional) Version of the software.
        :param uri: (Optional) URI the software can be found.
        '''
        if not generator is None:
            self.__rss_generator = generator + \
                (("/" + str(version)) if version is not None else "") + \
                ((" " + uri) if uri else "")
        return self.__rss_generator


    def image(self, url=None, title=None, link=None, width=None, height=None,
            description=None):
        '''Set the image of the feed.

        Don't confuse with itunes:image.

        :param url: The URL of a GIF, JPEG or PNG image.
        :param title: Describes the image. The default value is the feeds title.
        :param link: URL of the site the image will link to. The default is to
            use the feeds first altertate link.
        :param width: Width of the image in pixel. The maximum is 144.
        :param height: The height of the image. The maximum is 400.
        :param description: Title of the link.
        :returns: Data of the image as dictionary.
        '''
        if not url is None:
            self.__rss_image = { 'url' : url }
            if not title is None:
                self.__rss_image['title'] = title
            if not link is None:
                self.__rss_image['link'] = link
            if width:
                self.__rss_image['width'] = width
            if height:
                self.__rss_image['height'] = height
        return self.__rss_image


    def copyright(self, copyright=None):
        '''Get or set the copyright notice for content in the channel.

        :param copyright: The copyright notice.
        :returns: The copyright notice.
        '''

        if not copyright is None:
            self.__rss_copyright = copyright
        return self.__rss_copyright


    def description(self, description=None):
        '''Set and get the description of the feed,
        which is a phrase or sentence describing the channel. It is mandatory for
        RSS feeds.

        :param description: Description of the channel.
        :returns: Description of the channel.

        '''
        if not description is None:
            self.__rss_description = description
        return self.__rss_description


    def docs(self, docs=None):
        '''Get or set the docs value of the feed. It
        is a URL that points to the documentation for the format used in the RSS
        file. It is probably a pointer to [1]. It is for people who might stumble
        across an RSS file on a Web server 25 years from now and wonder what it
        is.

        [1]: http://www.rssboard.org/rss-specification

        :param docs: URL of the format documentation.
        :returns: URL of the format documentation.
        '''
        if not docs is None:
            self.__rss_docs = docs
        return self.__rss_docs


    def language(self, language=None):
        '''Get or set the language of the feed. It indicates the language the
        channel is written in. This allows aggregators to group all Italian
        language sites, for example, on a single page.
        The value should be an IETF language tag.

        :param language: Language of the feed.
        :returns: Language of the feed.
        '''
        if not language is None:
            self.__rss_language = language
        return self.__rss_language


    def managingEditor(self, managingEditor=None):
        '''Set or get the value for managingEditor which is the email address for
        person responsible for editorial content.

        :param managingEditor: Email adress of the managing editor.
        :returns: Email adress of the managing editor.
        '''
        if not managingEditor is None:
            self.__rss_managingEditor = managingEditor
        return self.__rss_managingEditor


    def pubDate(self, pubDate=None):
        '''Set or get the publication date for the content in the channel. For
        example, the New York Times publishes on a daily basis, the publication
        date flips once every 24 hours. That's when the pubDate of the channel
        changes.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        :param pubDate: The publication date.
        :returns: Publication date as datetime.datetime
        '''
        # TODO Add/rename to lastBuildDate
        if not pubDate is None:
            if isinstance(pubDate, string_types):
                pubDate = dateutil.parser.parse(pubDate)
            if not isinstance(pubDate, datetime):
                raise ValueError('Invalid datetime format')
            if pubDate.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__rss_pubDate = pubDate

        return self.__rss_pubDate


    def rating(self, rating=None):
        '''Set and get the PICS rating for the channel.
        '''
        if not rating is None:
            self.__rss_rating = rating
        return self.__rss_rating


    def skipHours(self, hours=None, replace=False):
        '''Set or get the value of skipHours, a hint for aggregators telling them
        which hours they can skip.

        This method can be called with an hour or a list of hours. The hours are
        represented as integer values from 0 to 23.

        :param hours:   List of hours the feedreaders should not check the feed.
        :param replace: Add or replace old data.
        :returns:       List of hours the feedreaders should not check the feed.
        '''
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
        '''Set or get the value of skipDays, a hint for aggregators telling them
        which days they can skip.

        This method can be called with a day name or a list of day names. The days are
        represented as strings from 'Monday' to 'Sunday'.

        :param hours:   List of days the feedreaders should not check the feed.
        :param replace: Add or replace old data.
        :returns:       List of days the feedreaders should not check the feed.
        '''
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


    def textInput(self, title=None, description=None, name=None, link=None):
        '''Get or set the value of textInput. The
        purpose of the <textInput> element is something of a mystery. You can use
        it to specify a search engine box. Or to allow a reader to provide
        feedback. Most aggregators ignore it.

        :param title: The label of the Submit button in the text input area.
        :param description: Explains the text input area.
        :param name: The name of the text object in the text input area.
        :param link: The URL of the CGI script that processes text input requests.
        :returns: Dictionary containing textInput values.
        '''
        if not title is None:
            self.__rss_textInput = {}
            self.__rss_textInput['title'] = title
            self.__rss_textInput['description'] = description
            self.__rss_textInput['name'] = name
            self.__rss_textInput['link'] = link
        return self.__rss_textInput


    def ttl(self, ttl=None):
        '''Get or set the ttl value. ttl stands for
        time to live. It's a number of minutes that indicates how long a channel
        can be cached before refreshing from the source.

        :param ttl: Integer value indicating how long the channel may be cached.
        :returns: Time to live.
        '''
        if not ttl is None:
            self.__rss_ttl = int(ttl)
        return self.__rss_ttl


    def webMaster(self, webMaster=None):
        '''Get and set the value of webMaster, which represents the email address
        for the person responsible for technical issues relating to the feed.

        :param webMaster: Email address of the webmaster.
        :returns: Email address of the webmaster.
        '''
        if not webMaster is None:
            self.__rss_webMaster = webMaster
        return self.__rss_webMaster

    def itunes_author(self, itunes_author=None):
        '''Get or set the itunes:author. The content of this tag is shown in the
        Artist column in iTunes. If the tag is not present, iTunes uses the
        contents of the <author> tag. If <itunes:author> is not present at the
        feed level, iTunes will use the contents of <managingEditor>.

        :param itunes_author: The author of the podcast.
        :type itunes_author: str
        :returns: The author of the podcast.
        '''
        if not itunes_author is None:
            self.__itunes_author = itunes_author
        return self.__itunes_author

    def itunes_block(self, itunes_block=None):
        '''Get or set the ITunes block attribute. Use this to prevent the entire
        podcast from appearing in the iTunes podcast directory.

        :param itunes_block: Block the podcast.
        :returns: If the podcast is blocked.
        '''
        if not itunes_block is None:
            self.__itunes_block = itunes_block
        return self.__itunes_block

    def itunes_category(self, itunes_category=None, itunes_subcategory=None):
        '''Get or set the ITunes category which appears in the category column
        and in iTunes Store Browser.

        The (sub-)category has to be one from the values defined at
        http://www.apple.com/itunes/podcasts/specs.html#categories

        :param itunes_category: Category of the podcast, unescaped.
        :type itunes_category: str
        :param itunes_subcategory: Subcategory of the podcast, unescaped. The subcategory need not be set.
        :type itunes_subcategory: str
        :returns: Dictionary which has category with key 'cat', and optionally subcategory with key 'sub'.
        '''
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

    def itunes_image(self, itunes_image=None):
        '''Get or set the image for the podcast. This tag specifies the artwork
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
        '''
        if not itunes_image is None:
            lowercase_itunes_image = itunes_image.lower()
            if not (lowercase_itunes_image.endswith(('.jpg', '.jpeg', '.png'))):
                raise ValueError('Image filename must end with png or jpg, not .%s' % itunes_image.split(".")[-1])
            self.__itunes_image = itunes_image
        return self.__itunes_image

    def itunes_explicit(self, itunes_explicit=None):
        '''Get or the the itunes:explicit value of the podcast. This tag should
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
        '''
        if not itunes_explicit is None:
            if not itunes_explicit in ('', 'yes', 'no', 'clean'):
                raise ValueError('Invalid value "%s" for explicit tag' % itunes_explicit)
            self.__itunes_explicit = itunes_explicit
        return self.__itunes_explicit

    def itunes_complete(self, itunes_complete=None):
        '''Get or set the itunes:complete value of the podcast. This tag can be
        used to indicate the completion of a podcast.

        If you populate this tag with "yes", you are indicating that no more
        episodes will be added to the podcast. If the &lt;itunes:complete&gt; tag is
        present and has any other value (e.g. “no”), it will have no effect on
        the podcast.

        :param itunes_complete: If the podcast is complete.
        :type itunes_complete: bool or str
        :returns: If the podcast is complete.
        '''
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
        '''Get or set the new-feed-url property of the podcast. This tag allows
        you to change the URL where the podcast feed is located

        After adding the tag to your old feed, you should maintain the old feed
        for 48 hours before retiring it. At that point, iTunes will have updated
        the directory with the new feed URL.

        :param itunes_new_feed_url: New feed URL.
        :type itunes_new_feed_url: str
        :returns: New feed URL.
        '''
        if not itunes_new_feed_url is None:
            self.__itunes_new_feed_url = itunes_new_feed_url
        return self.__itunes_new_feed_url

    def itunes_owner(self, name=None, email=None):
        '''Get or set the itunes:owner of the podcast. This tag contains
        information that will be used to contact the owner of the podcast for
        communication specifically about the podcast. It will not be publicly
        displayed.

        Both the name and email are required; you cannot use one or the other alone.

        :param name: The name of the owner of the feed.
        :type name: str
        :param email: The feed owner's email.
        :type email: str
        :returns: Data of the owner of the feed.
        '''
        if not name is None:
            if name and email:
                self.__itunes_owner = {'name': name, 'email': email}
            elif not name and not email:
                self.__itunes_owner = None
            else:
                raise ValueError('Both name and email have to be set.')
        return self.__itunes_owner

    def itunes_subtitle(self, itunes_subtitle=None):
        '''Get or set the itunes:subtitle value for the podcast. The contents of
        this tag are shown in the Description column in iTunes. The subtitle
        displays best if it is only a few words long.

        :param itunes_subtitle: Subtitle of the podcast.
        :type itunes_subtitle: str
        :returns: Subtitle of the podcast.
        '''
        if not itunes_subtitle is None:
            self.__itunes_subtitle = itunes_subtitle
        return self.__itunes_subtitle

    def itunes_summary(self, itunes_summary=None):
        '''Get or set the itunes:summary value for the podcast. The contents of
        this tag are shown in a separate window that appears when the "circled i"
        in the Description column is clicked. It also appears on the iTunes page
        for your podcast. This field can be up to 4000 characters. If
        <itunes:summary> is not included, the contents of the <description> tag
        are used.

        :param itunes_summary: Summary of the podcast.
        :type itunes_summary: str
        :returns: Summary of the podcast.
        '''
        if not itunes_summary is None:
            self.__itunes_summary = itunes_summary
        return self.__itunes_summary

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

    def add_entry(self, feedEntry=None):
        '''This method will add a new entry to the feed. If the feedEntry
        argument is omittet a new Entry object is created automatically. This is
        the prefered way to add new entries to a feed.

        :param feedEntry: FeedEntry object to add.
        :returns: FeedEntry object created or passed to this function.

        Example::

            ...
            >>> entry = feedgen.add_entry()
            >>> entry.title('First feed entry')

        '''
        if feedEntry is None:
            feedEntry = FeedEntry()

        version = sys.version_info[0]

        if version == 2:
            items = self.__extensions.iteritems()
        else:
            items = self.__extensions.items()

        # Try to load extensions:
        for extname,ext in items:
            try:
                feedEntry.load_extension( extname, ext['atom'], ext['rss'] )
            except ImportError:
                pass

        self.__feed_entries.append( feedEntry )
        return feedEntry


    def add_item(self, item=None):
        '''This method will add a new item to the feed. If the item argument is
        omittet a new FeedEntry object is created automatically. This is just
        another name for add_entry(...)
        '''
        return self.add_entry(item)


    def entry(self, entry=None, replace=False):
        '''Get or set feed entries. Use the add_entry() method instead to
        automatically create the FeedEntry objects.

        This method takes both a single FeedEntry object or a list of objects.

        :param entry: FeedEntry object or list of FeedEntry objects.
        :returns: List ob all feed entries.
        '''
        if not entry is None:
            if not isinstance(entry, list):
                entry = [entry]
            if replace:
                self.__feed_entries = []

            version = sys.version_info[0]

            if version == 2:
                items = self.__extensions.iteritems()
            else:
                items = self.__extensions.items()

            # Try to load extensions:
            for e in entry:
                for extname,ext in items:
                    try:
                        e.load_extension( extname, ext['atom'], ext['rss'] )
                    except ImportError:
                        pass

            self.__feed_entries += entry
        return self.__feed_entries


    def item(self, item=None, replace=False):
        '''Get or set feed items. This is just another name for entry(...)
        '''
        return self.entry(item, replace)


    def remove_entry(self, entry):
        '''Remove a single entry from the feed. This method accepts both the
        FeedEntry object to remove or the index of the entry as argument.

        :param entry: Entry or index of entry to remove.
        '''
        if isinstance(entry, FeedEntry):
            self.__feed_entries.remove(entry)
        else:
            self.__feed_entries.pop(entry)


    def remove_item(self, item):
        '''Remove a single item from the feed. This is another name for
        remove_entry.
        '''
        self.remove_entry(item)


    def load_extension(self, name):
        '''Load a specific extension by name.

        :param name: Name of the extension to load.
        :param rss: If the extension should be used for RSS feeds.
        '''
        # Check loaded extensions
        if not isinstance(self.__extensions, dict):
            self.__extensions = {}
        if name in self.__extensions.keys():
            raise ImportError('Extension already loaded')

        # Load extension
        extname = name[0].upper() + name[1:] + 'Extension'
        supmod = __import__('feedgen.ext.%s' % name)
        extmod = getattr(supmod.ext, name)
        ext    = getattr(extmod, extname)
        extinst = ext()
        setattr(self, name, extinst)
        self.__extensions[name] = {'inst':extinst}

        # Try to load the extension for already existing entries:
        for entry in self.__feed_entries:
            try:
                entry.load_extension( name)
            except ImportError:
                pass
