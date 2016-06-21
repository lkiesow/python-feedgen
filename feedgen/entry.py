# -*- coding: utf-8 -*-
'''
    feedgen.entry
    ~~~~~~~~~~~~~

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
'''
import collections

from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from feedgen.util import ensure_format, formatRFC2822
from feedgen.compat import string_types


class FeedEntry(object):
    '''FeedEntry call representing an ATOM feeds entry node or an RSS feeds item
    node.
    '''

    def __init__(self):
        # RSS
        self.__rss_author      = None
        self.__rss_category    = None
        self.__rss_comments    = None
        self.__rss_description = None
        self.__rss_content     = None
        self.__rss_enclosure   = None
        self.__rss_guid        = None
        self.__rss_link        = None
        self.__rss_pubDate     = None
        self.__rss_source      = None
        self.__rss_title       = None

        # Extension list:
        self.__extensions = {}


    def rss_entry(self, extensions=True):
        '''Create a RSS item and return it.'''
        entry = etree.Element('item')
        if not ( self.__rss_title or self.__rss_description or self.__rss_content):
            raise ValueError('Required fields not set')
        if self.__rss_title:
            title = etree.SubElement(entry, 'title')
            title.text = self.__rss_title
        if self.__rss_link:
            link = etree.SubElement(entry, 'link')
            link.text = self.__rss_link
        if self.__rss_description and self.__rss_content:
            description = etree.SubElement(entry, 'description')
            description.text = self.__rss_description
            content = etree.SubElement(entry, '{%s}encoded' %
                                    'http://purl.org/rss/1.0/modules/content/')
            content.text = etree.CDATA(self.__rss_content['content']) \
                if self.__rss_content.get('type', '') == 'CDATA' else self.__rss_content['content']
        elif self.__rss_description:
            description = etree.SubElement(entry, 'description')
            description.text = self.__rss_description
        elif self.__rss_content:
            description = etree.SubElement(entry, 'description')
            description.text = self.__rss_content['content']
        for a in self.__rss_author or []:
            author = etree.SubElement(entry, 'author')
            author.text = a
        if self.__rss_guid:
            guid = etree.SubElement(entry, 'guid')
            guid.text = self.__rss_guid
            guid.attrib['isPermaLink'] = 'false'
        for cat in self.__rss_category or []:
            category = etree.SubElement(entry, 'category')
            category.text = cat['value']
            if cat.get('domain'):
                category.attrib['domain'] = cat['domain']
        if self.__rss_comments:
            comments = etree.SubElement(entry, 'comments')
            comments.text = self.__rss_comments
        if self.__rss_enclosure:
            enclosure = etree.SubElement(entry, 'enclosure')
            enclosure.attrib['url'] = self.__rss_enclosure['url']
            enclosure.attrib['length'] = self.__rss_enclosure['length']
            enclosure.attrib['type'] = self.__rss_enclosure['type']
        if self.__rss_pubDate:
            pubDate = etree.SubElement(entry, 'pubDate')
            pubDate.text = formatRFC2822(self.__rss_pubDate)

        if extensions:
            for ext in self.__extensions.values() or []:
                ext['inst'].extend_rss(entry)

        return entry



    def title(self, title=None):
        '''Get or set the title value of the entry. It should contain a human
        readable title for the entry. Title is mandatory and should not be blank.

        :param title: The new title of the entry.
        :returns: The entriess title.
        '''
        if not title is None:
            self.__rss_title = title
        return self.__rss_title


    def guid(self, guid=None):
        '''Get or set the entries guid which is a string that uniquely identifies
        the item.

        :param guid: Id of the entry.
        :returns: Id of the entry.
        '''
        if not guid is None:
            self.__rss_guid = guid
        return self.__rss_guid


    def author(self, author=None, replace=False, **kwargs):
        '''Get or set autor data. An author element is a dict containing a name and
        an email adress. Email is mandatory.

        This method can be called with:
        - the fields of an author as keyword arguments
        - the fields of an author as a dictionary
        - a list of dictionaries containing the author fields

        An author has the following fields:
        - *name* conveys a human-readable name for the person.
        - *email* contains an email address for the person.

        :param author:  Dict or list of dicts with author data.
        :param replace: Add or replace old data.

        Example::

            >>> author( { 'name':'John Doe', 'email':'jdoe@example.com' } )
            [{'name':'John Doe','email':'jdoe@example.com'}]

            >>> author([{'name':'Mr. X'},{'name':'Max'}])
            [{'name':'John Doe','email':'jdoe@example.com'},
                    {'name':'John Doe'}, {'name':'Max'}]

            >>> author( name='John Doe', email='jdoe@example.com', replace=True )
            [{'name':'John Doe','email':'jdoe@example.com'}]

        '''
        if author is None and kwargs:
            author = kwargs
        if not author is None:
            if replace or self.__rss_author is None:
                self.__rss_author = []
            authors = ensure_format( author,
                    set(['name', 'email']), set(['email']))
            self.__rss_author += ['%s (%s)' % ( a['email'], a['name'] ) for a in authors]
        return self.__rss_author


    def content(self, content=None, type=None):
        '''Get or set the content of the entry which contains or links to the
        complete content of the entry. If the content is set (not linked) it will also set
        rss:description.

        :param content: The content of the feed entry.
        :param src: Link to the entries content.
        :param type: If type is CDATA content would not be escaped.
        :returns: Content element of the entry.
        '''
        if not content is None:
            self.__rss_content = {'content':content}
            if not type is None:
                self.__rss_content['type'] = type
        return self.__rss_content


    def link(self, href=None):
        '''Get or set the link to the full version of this episode description.

        :param href: the URI of the referenced resource (typically a Web page)
        :returns: The current link URI.
        '''
        if not href is None:
            self.__rss_link = href
        return self.__rss_link


    def description(self, description=None):
        '''Get or set the description value which is the item synopsis.

        :param description: Description of the entry.
        :returns: The entries description.
        '''
        if not description is None:
            self.__rss_description = description
        return self.__rss_description

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
                self.__rss_category.append(rss_cat)
        return self.__rss_category


    def published(self, published=None):
        '''Set or get the published value which contains the time of the initial
        creation or first availability of the entry.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        :param published: The creation date.
        :returns: Creation date as datetime.datetime
        '''
        if not published is None:
            if isinstance(published, string_types):
                published = dateutil.parser.parse(published)
            if not isinstance(published, datetime):
                raise ValueError('Invalid datetime format')
            if published.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__rss_pubDate = published

        return self.__rss_pubDate


    def pubdate(self, pubDate=None):
        '''Get or set the pubDate of the entry which indicates when the entry was
        published. This method is just another name for the published(...)
        method.
        '''
        return self.published(pubDate)


    def comments(self, comments=None):
        '''Get or set the the value of comments which is the url of the comments
        page for the item.

        :param comments: URL to the comments page.
        :returns: URL to the comments page.
        '''
        if not comments is None:
            self.__rss_comments = comments
        return self.__rss_comments


    def enclosure(self, url=None, length=None, type=None):
        '''Get or set the value of enclosure which describes a media object that
        is attached to this item.

        :param url: URL of the media object.
        :param length: Size of the media in bytes.
        :param type: Mimetype of the linked media.
        :returns: Data of the enclosure element.
        '''
        if not url is None:
            self.__rss_enclosure = {'url': url, 'length': length, 'type': type}
        return self.__rss_enclosure


    def load_extension(self, name):
        '''Load a specific extension by name.

        :param name: Name of the extension to load.
        '''
        # Check loaded extensions
        if not isinstance(self.__extensions, dict):
            self.__extensions = {}
        if name in self.__extensions.keys():
            raise ImportError('Extension already loaded')

        # Load extension
        extname = name[0].upper() + name[1:] + 'EntryExtension'

        # Try to import extension from dedicated module for entry:
        try:
            supmod = __import__('feedgen.ext.%s_entry' % name)
            extmod = getattr(supmod.ext, name + '_entry')
        except ImportError:
            # Try the FeedExtension module instead
            supmod = __import__('feedgen.ext.%s' % name)
            extmod = getattr(supmod.ext, name)

        ext    = getattr(extmod, extname)
        extinst = ext()
        setattr(self, name, extinst)
        self.__extensions[name] = {'inst':extinst}
