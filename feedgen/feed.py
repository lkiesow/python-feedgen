# -*- coding: utf-8 -*-
'''
    feedgen.feed
    ~~~~~~~~~~~~

    :copyright: 2013-2020, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.

'''

import sys
from datetime import datetime

import dateutil.parser
import dateutil.tz
from lxml import etree  # nosec - not using this for parsing

import feedgen.version
from feedgen.compat import string_types
from feedgen.entry import FeedEntry
from feedgen.util import ensure_format, formatRFC2822, xml_elem

_feedgen_version = feedgen.version.version_str


class FeedGenerator(object):
    '''FeedGenerator for generating ATOM and RSS feeds.
    '''

    def __init__(self):
        self.__feed_entries = []

        # ATOM
        # https://tools.ietf.org/html/rfc4287
        # required
        self.__atom_id = None
        self.__atom_title = None
        self.__atom_updated = datetime.now(dateutil.tz.tzutc())

        # recommended
        self.__atom_author = None  # {name*, uri, email}
        self.__atom_link = None  # {href*, rel, type, hreflang, title, length}

        # optional
        self.__atom_category = None  # {term*, scheme, label}
        self.__atom_contributor = None
        self.__atom_generator = {
                'value': 'python-feedgen',
                'uri': 'https://lkiesow.github.io/python-feedgen',
                'version': feedgen.version.version_str}  # {value*,uri,version}
        self.__atom_icon = None
        self.__atom_logo = None
        self.__atom_rights = None
        self.__atom_subtitle = None

        # other
        self.__atom_feed_xml_lang = None

        # RSS
        # http://www.rssboard.org/rss-specification
        self.__rss_title = None
        self.__rss_link = None
        self.__rss_description = None

        self.__rss_category = None
        self.__rss_cloud = None
        self.__rss_copyright = None
        self.__rss_docs = 'http://www.rssboard.org/rss-specification'
        self.__rss_generator = 'python-feedgen'
        self.__rss_image = None
        self.__rss_language = None
        self.__rss_lastBuildDate = datetime.now(dateutil.tz.tzutc())
        self.__rss_managingEditor = None
        self.__rss_pubDate = None
        self.__rss_rating = None
        self.__rss_skipHours = None
        self.__rss_skipDays = None
        self.__rss_textInput = None
        self.__rss_ttl = None
        self.__rss_webMaster = None

        # Extension list:
        self.__extensions = {}

    def _create_atom(self, extensions=True):
        '''Create a ATOM feed xml structure containing all previously set
        fields.

        :returns: Tuple containing the feed root element and the element tree.
        '''
        nsmap = dict()
        if extensions:
            for ext in self.__extensions.values() or []:
                if ext.get('atom'):
                    nsmap.update(ext['inst'].extend_ns())

        feed = xml_elem('feed',
                        xmlns='http://www.w3.org/2005/Atom',
                        nsmap=nsmap)
        if self.__atom_feed_xml_lang:
            feed.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = \
                    self.__atom_feed_xml_lang

        if not (self.__atom_id and self.__atom_title and self.__atom_updated):
            missing = ([] if self.__atom_title else ['title']) + \
                      ([] if self.__atom_id else ['id']) + \
                      ([] if self.__atom_updated else ['updated'])
            missing = ', '.join(missing)
            raise ValueError('Required fields not set (%s)' % missing)
        id = xml_elem('id', feed)
        id.text = self.__atom_id
        title = xml_elem('title', feed)
        title.text = self.__atom_title
        updated = xml_elem('updated', feed)
        updated.text = self.__atom_updated.isoformat()

        # Add author elements
        for a in self.__atom_author or []:
            # Atom requires a name. Skip elements without.
            if not a.get('name'):
                continue
            author = xml_elem('author', feed)
            name = xml_elem('name', author)
            name.text = a.get('name')
            if a.get('email'):
                email = xml_elem('email', author)
                email.text = a.get('email')
            if a.get('uri'):
                uri = xml_elem('uri', author)
                uri.text = a.get('uri')

        for l in self.__atom_link or []:
            link = xml_elem('link', feed, href=l['href'])
            if l.get('rel'):
                link.attrib['rel'] = l['rel']
            if l.get('type'):
                link.attrib['type'] = l['type']
            if l.get('hreflang'):
                link.attrib['hreflang'] = l['hreflang']
            if l.get('title'):
                link.attrib['title'] = l['title']
            if l.get('length'):
                link.attrib['length'] = l['length']

        for c in self.__atom_category or []:
            cat = xml_elem('category', feed, term=c['term'])
            if c.get('scheme'):
                cat.attrib['scheme'] = c['scheme']
            if c.get('label'):
                cat.attrib['label'] = c['label']

        # Add author elements
        for c in self.__atom_contributor or []:
            # Atom requires a name. Skip elements without.
            if not c.get('name'):
                continue
            contrib = xml_elem('contributor', feed)
            name = xml_elem('name', contrib)
            name.text = c.get('name')
            if c.get('email'):
                email = xml_elem('email', contrib)
                email.text = c.get('email')
            if c.get('uri'):
                uri = xml_elem('uri', contrib)
                uri.text = c.get('uri')

        if self.__atom_generator and self.__atom_generator.get('value'):
            generator = xml_elem('generator', feed)
            generator.text = self.__atom_generator['value']
            if self.__atom_generator.get('uri'):
                generator.attrib['uri'] = self.__atom_generator['uri']
            if self.__atom_generator.get('version'):
                generator.attrib['version'] = self.__atom_generator['version']

        if self.__atom_icon:
            icon = xml_elem('icon', feed)
            icon.text = self.__atom_icon

        if self.__atom_logo:
            logo = xml_elem('logo', feed)
            logo.text = self.__atom_logo

        if self.__atom_rights:
            rights = xml_elem('rights', feed)
            rights.text = self.__atom_rights

        if self.__atom_subtitle:
            subtitle = xml_elem('subtitle', feed)
            subtitle.text = self.__atom_subtitle

        if extensions:
            for ext in self.__extensions.values() or []:
                if ext.get('atom'):
                    ext['inst'].extend_atom(feed)

        for entry in self.__feed_entries:
            entry = entry.atom_entry()
            feed.append(entry)

        doc = etree.ElementTree(feed)
        return feed, doc

    def atom_str(self, pretty=False, extensions=True, encoding='UTF-8',
                 xml_declaration=True):
        '''Generates an ATOM feed and returns the feed XML as string.

        :param pretty: If the feed should be split into multiple lines and
            properly indented.
        :param extensions: Enable or disable the loaded extensions for the xml
            generation (default: enabled).
        :param encoding: Encoding used in the  XML file (default: UTF-8).
        :param xml_declaration: If an XML declaration should be added to the
            output (Default: enabled).
        :returns: String representation of the ATOM feed.

        **Return type:** The return type may vary between different Python
        versions and your encoding parameters passed to this method. For
        details have a look at the `lxml documentation
        <https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.tostring>`_
        '''
        feed, doc = self._create_atom(extensions=extensions)
        return etree.tostring(feed, pretty_print=pretty, encoding=encoding,
                              xml_declaration=xml_declaration)

    def atom_file(self, filename, extensions=True, pretty=False,
                  encoding='UTF-8', xml_declaration=True):
        '''Generates an ATOM feed and write the resulting XML to a file.

        :param filename: Name of file to write or a file-like object or a URL.
        :param extensions: Enable or disable the loaded extensions for the xml
            generation (default: enabled).
        :param pretty: If the feed should be split into multiple lines and
            properly indented.
        :param encoding: Encoding used in the  XML file (default: UTF-8).
        :param xml_declaration: If an XML declaration should be added to the
            output (Default: enabled).
        '''
        feed, doc = self._create_atom(extensions=extensions)
        doc.write(filename, pretty_print=pretty, encoding=encoding,
                  xml_declaration=xml_declaration)

    def _create_rss(self, extensions=True):
        '''Create an RSS feed xml structure containing all previously set
        fields.

        :returns: Tuple containing the feed root element and the element tree.
        '''
        nsmap = dict()
        if extensions:
            for ext in self.__extensions.values() or []:
                if ext.get('rss'):
                    nsmap.update(ext['inst'].extend_ns())

        nsmap.update({'atom':  'http://www.w3.org/2005/Atom',
                      'content': 'http://purl.org/rss/1.0/modules/content/'})

        feed = xml_elem('rss', version='2.0', nsmap=nsmap)
        channel = xml_elem('channel', feed)
        if not (self.__rss_title and
                self.__rss_link and
                self.__rss_description):
            missing = ([] if self.__rss_title else ['title']) + \
                      ([] if self.__rss_link else ['link']) + \
                      ([] if self.__rss_description else ['description'])
            missing = ', '.join(missing)
            raise ValueError('Required fields not set (%s)' % missing)
        title = xml_elem('title', channel)
        title.text = self.__rss_title
        link = xml_elem('link', channel)
        link.text = self.__rss_link
        desc = xml_elem('description', channel)
        desc.text = self.__rss_description
        for ln in self.__atom_link or []:
            # It is recommended to include a atom self link in rss documents…
            if ln.get('rel') == 'self':
                selflink = xml_elem('{http://www.w3.org/2005/Atom}link',
                                    channel, href=ln['href'], rel='self')
                if ln.get('type'):
                    selflink.attrib['type'] = ln['type']
                if ln.get('hreflang'):
                    selflink.attrib['hreflang'] = ln['hreflang']
                if ln.get('title'):
                    selflink.attrib['title'] = ln['title']
                if ln.get('length'):
                    selflink.attrib['length'] = ln['length']
                break
        if self.__rss_category:
            for cat in self.__rss_category:
                category = xml_elem('category', channel)
                category.text = cat['value']
                if cat.get('domain'):
                    category.attrib['domain'] = cat['domain']
        if self.__rss_cloud:
            cloud = xml_elem('cloud', channel)
            cloud.attrib['domain'] = self.__rss_cloud.get('domain')
            cloud.attrib['port'] = self.__rss_cloud.get('port')
            cloud.attrib['path'] = self.__rss_cloud.get('path')
            cloud.attrib['registerProcedure'] = self.__rss_cloud.get(
                    'registerProcedure')
            cloud.attrib['protocol'] = self.__rss_cloud.get('protocol')
        if self.__rss_copyright:
            copyright = xml_elem('copyright', channel)
            copyright.text = self.__rss_copyright
        if self.__rss_docs:
            docs = xml_elem('docs', channel)
            docs.text = self.__rss_docs
        if self.__rss_generator:
            generator = xml_elem('generator', channel)
            generator.text = self.__rss_generator
        if self.__rss_image:
            image = xml_elem('image', channel)
            url = xml_elem('url', image)
            url.text = self.__rss_image.get('url')
            title = xml_elem('title', image)
            title.text = self.__rss_image.get('title', self.__rss_title)
            link = xml_elem('link', image)
            link.text = self.__rss_image.get('link', self.__rss_link)
            if self.__rss_image.get('width'):
                width = xml_elem('width', image)
                width.text = self.__rss_image.get('width')
            if self.__rss_image.get('height'):
                height = xml_elem('height', image)
                height.text = self.__rss_image.get('height')
            if self.__rss_image.get('description'):
                description = xml_elem('description', image)
                description.text = self.__rss_image.get('description')
        if self.__rss_language:
            language = xml_elem('language', channel)
            language.text = self.__rss_language
        if self.__rss_lastBuildDate:
            lastBuildDate = xml_elem('lastBuildDate', channel)

            lastBuildDate.text = formatRFC2822(self.__rss_lastBuildDate)
        if self.__rss_managingEditor:
            managingEditor = xml_elem('managingEditor', channel)
            managingEditor.text = self.__rss_managingEditor
        if self.__rss_pubDate:
            pubDate = xml_elem('pubDate', channel)
            pubDate.text = formatRFC2822(self.__rss_pubDate)
        if self.__rss_rating:
            rating = xml_elem('rating', channel)
            rating.text = self.__rss_rating
        if self.__rss_skipHours:
            skipHours = xml_elem('skipHours', channel)
            for h in self.__rss_skipHours:
                hour = xml_elem('hour', skipHours)
                hour.text = str(h)
        if self.__rss_skipDays:
            skipDays = xml_elem('skipDays', channel)
            for d in self.__rss_skipDays:
                day = xml_elem('day', skipDays)
                day.text = d
        if self.__rss_textInput:
            textInput = xml_elem('textInput', channel)
            textInput.attrib['title'] = self.__rss_textInput.get('title')
            textInput.attrib['description'] = \
                self.__rss_textInput.get('description')
            textInput.attrib['name'] = self.__rss_textInput.get('name')
            textInput.attrib['link'] = self.__rss_textInput.get('link')
        if self.__rss_ttl:
            ttl = xml_elem('ttl', channel)
            ttl.text = str(self.__rss_ttl)
        if self.__rss_webMaster:
            webMaster = xml_elem('webMaster', channel)
            webMaster.text = self.__rss_webMaster

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
        :param extensions: Enable or disable the loaded extensions for the xml
            generation (default: enabled).
        :param encoding: Encoding used in the  XML file (default: UTF-8).
        :param xml_declaration: If an XML declaration should be added to the
            output (Default: enabled).
        :returns: String representation of the RSS feed.

        **Return type:** The return type may vary between different Python
        versions and your encoding parameters passed to this method. For
        details have a look at the `lxml documentation
        <https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.tostring>`_
        '''
        feed, doc = self._create_rss(extensions=extensions)
        return etree.tostring(feed, pretty_print=pretty, encoding=encoding,
                              xml_declaration=xml_declaration)

    def rss_file(self, filename, extensions=True, pretty=False,
                 encoding='UTF-8', xml_declaration=True):
        '''Generates an RSS feed and write the resulting XML to a file.

        :param filename: Name of file to write or a file-like object or a URL.
        :param extensions: Enable or disable the loaded extensions for the xml
            generation (default: enabled).
        :param pretty: If the feed should be split into multiple lines and
            properly indented.
        :param encoding: Encoding used in the  XML file (default: UTF-8).
        :param xml_declaration: If an XML declaration should be added to the
            output (Default: enabled).
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
        :returns: The feeds title.
        '''
        if title is not None:
            self.__atom_title = title
            self.__rss_title = title
        return self.__atom_title

    def id(self, id=None):
        '''Get or set the feed id which identifies the feed using a universally
        unique and permanent URI. If you have a long-term, renewable lease on
        your Internet domain name, then you can feel free to use your website's
        address. This field is for ATOM only. It is mandatory for ATOM.

        :param id: New Id of the ATOM feed.
        :returns: Id of the feed.
        '''

        if id is not None:
            self.__atom_id = id
        return self.__atom_id

    def updated(self, updated=None):
        '''Set or get the updated value which indicates the last time the feed
        was modified in a significant way.

        The value can either be a string which will automatically be parsed or
        a datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        This will set both atom:updated and rss:lastBuildDate.

        Default value
            If not set, updated has as value the current date and time.

        :param updated: The modification date.
        :returns: Modification date as datetime.datetime
        '''
        if updated is not None:
            if isinstance(updated, string_types):
                updated = dateutil.parser.parse(updated)
            if not isinstance(updated, datetime):
                raise ValueError('Invalid datetime format')
            if updated.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__atom_updated = updated
            self.__rss_lastBuildDate = updated

        return self.__atom_updated

    def lastBuildDate(self, lastBuildDate=None):
        '''Set or get the lastBuildDate value which indicates the last time the
        content of the channel changed.

        The value can either be a string which will automatically be parsed or
        a datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        This will set both atom:updated and rss:lastBuildDate.

        Default value
            If not set, lastBuildDate has as value the current date and time.

        :param lastBuildDate: The modification date.
        :returns: Modification date as datetime.datetime
        '''
        return self.updated(lastBuildDate)

    def author(self, author=None, replace=False, **kwargs):
        '''Get or set author data. An author element is a dictionary containing
        a name, an email address and a URI. Name is mandatory for ATOM, email
        is mandatory for RSS.

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

            >>> feedgen.author({'name':'John Doe', 'email':'jdoe@example.com'})
            [{'name':'John Doe','email':'jdoe@example.com'}]

            >>> feedgen.author([{'name':'Mr. X'},{'name':'Max'}])
            [{'name':'John Doe','email':'jdoe@example.com'},
                    {'name':'John Doe'}, {'name':'Max'}]

            >>> feedgen.author(name='John Doe', email='jdoe@example.com',
                               replace=True)
            [{'name':'John Doe','email':'jdoe@example.com'}]

        '''
        if author is None and kwargs:
            author = kwargs
        if author is not None:
            if replace or self.__atom_author is None:
                self.__atom_author = []
            self.__atom_author += ensure_format(author,
                                                set(['name', 'email', 'uri']),
                                                set(['name']))
            self.__rss_author = []
            for a in self.__atom_author:
                if a.get('email'):
                    self.__rss_author.append(a['email'])
        return self.__atom_author

    def link(self, link=None, replace=False, **kwargs):
        '''Get or set link data. An link element is a dict with the fields
        href, rel, type, hreflang, title, and length. Href is mandatory for
        ATOM.

        This method can be called with:

        - the fields of a link as keyword arguments
        - the fields of a link as a dictionary
        - a list of dictionaries containing the link fields

        A link has the following fields:

        - *href* is the URI of the referenced resource (typically a Web page)
        - *rel* contains a single link relationship type. It can be a full URI,
          or one of the following predefined values (default=alternate):

            - *alternate* an alternate representation of the entry or feed, for
              example a permalink to the html version of the entry, or the
              front page of the weblog.
            - *enclosure* a related resource which is potentially large in size
              and might require special handling, for example an audio or video
              recording.
            - *related* an document related to the entry or feed.
            - *self* the feed itself.
            - *via* the source of the information provided in the entry.

        - *type* indicates the media type of the resource.
        - *hreflang* indicates the language of the referenced resource.
        - *title* human readable information about the link, typically for
          display purposes.
        - *length* the length of the resource, in bytes.

        RSS only supports one link with URL only.

        :param link:    Dict or list of dicts with data.
        :param replace: If old links are to be replaced (default: False)
        :returns:       Current set of link data

        Example::

            >>> feedgen.link( href='http://example.com/', rel='self')
            [{'href':'http://example.com/', 'rel':'self'}]

        '''
        if link is None and kwargs:
            link = kwargs
        if link is not None:
            if replace or self.__atom_link is None:
                self.__atom_link = []
            self.__atom_link += ensure_format(
                link,
                set(['href', 'rel', 'type', 'hreflang', 'title', 'length']),
                set(['href']),
                {'rel': [
                    'about', 'alternate', 'appendix', 'archives', 'author',
                    'bookmark', 'canonical', 'chapter', 'collection',
                    'contents', 'copyright', 'create-form', 'current',
                    'derivedfrom', 'describedby', 'describes', 'disclosure',
                    'duplicate', 'edit', 'edit-form', 'edit-media',
                    'enclosure', 'first', 'glossary', 'help', 'hosts', 'hub',
                    'icon', 'index', 'item', 'last', 'latest-version',
                    'license', 'lrdd', 'memento', 'monitor', 'monitor-group',
                    'next', 'next-archive', 'nofollow', 'noreferrer',
                    'original', 'payment', 'predecessor-version', 'prefetch',
                    'prev', 'preview', 'previous', 'prev-archive',
                    'privacy-policy', 'profile', 'related', 'replies',
                    'search', 'section', 'self', 'service', 'start',
                    'stylesheet', 'subsection', 'successor-version', 'tag',
                    'terms-of-service', 'timegate', 'timemap', 'type', 'up',
                    'version-history', 'via', 'working-copy', 'working-copy-of'
                    ]})
            # RSS only needs one URL. We use the first link for RSS:
            if len(self.__atom_link) > 0:
                self.__rss_link = self.__atom_link[-1]['href']
        # return the set with more information (atom)
        return self.__atom_link

    def category(self, category=None, replace=False, **kwargs):
        '''Get or set categories that the feed belongs to.

        This method can be called with:

        - the fields of a category as keyword arguments
        - the fields of a category as a dictionary
        - a list of dictionaries containing the category fields

        A categories has the following fields:

        - *term* identifies the category
        - *scheme* identifies the categorization scheme via a URI.
        - *label* provides a human-readable label for display

        If a label is present it is used for the RSS feeds. Otherwise the term
        is used. The scheme is used for the domain attribute in RSS.

        :param link:    Dict or list of dicts with data.
        :param replace: Add or replace old data.
        :returns: List of category data.
        '''
        if category is None and kwargs:
            category = kwargs
        if category is not None:
            if replace or self.__atom_category is None:
                self.__atom_category = []
            self.__atom_category += ensure_format(
                    category,
                    set(['term', 'scheme', 'label']),
                    set(['term']))
            # Map the ATOM categories to RSS categories. Use the atom:label as
            # name or if not present the atom:term. The atom:scheme is the
            # rss:domain.
            self.__rss_category = []
            for cat in self.__atom_category:
                rss_cat = {}
                rss_cat['value'] = cat.get('label', cat['term'])
                if cat.get('scheme'):
                    rss_cat['domain'] = cat['scheme']
                self.__rss_category.append(rss_cat)
        return self.__atom_category

    def cloud(self, domain=None, port=None, path=None, registerProcedure=None,
              protocol=None):
        '''Set or get the cloud data of the feed. It is an RSS only attribute.
        It specifies a web service that supports the rssCloud interface which
        can be implemented in HTTP-POST, XML-RPC or SOAP 1.1.

        :param domain: The domain where the webservice can be found.
        :param port: The port the webservice listens to.
        :param path: The path of the webservice.
        :param registerProcedure: The procedure to call.
        :param protocol: Can be either HTTP-POST, XML-RPC or SOAP 1.1.
        :returns: Dictionary containing the cloud data.
        '''
        if domain is not None:
            self.__rss_cloud = {'domain': domain, 'port': port, 'path': path,
                                'registerProcedure': registerProcedure,
                                'protocol': protocol}
        return self.__rss_cloud

    def contributor(self, contributor=None, replace=False, **kwargs):
        '''Get or set the contributor data of the feed. This is an ATOM only
        value.

        This method can be called with:
        - the fields of an contributor as keyword arguments
        - the fields of an contributor as a dictionary
        - a list of dictionaries containing the contributor fields

        An contributor has the following fields:
        - *name* conveys a human-readable name for the person.
        - *uri* contains a home page for the person.
        - *email* contains an email address for the person.

        :param contributor: Dictionary or list of dictionaries with contributor
                            data.
        :param replace: Add or replace old data.
        :returns: List of contributors as dictionaries.
        '''
        if contributor is None and kwargs:
            contributor = kwargs
        if contributor is not None:
            if replace or self.__atom_contributor is None:
                self.__atom_contributor = []
            self.__atom_contributor += ensure_format(
                    contributor, set(['name', 'email', 'uri']), set(['name']))
        return self.__atom_contributor

    def generator(self, generator=None, version=None, uri=None):
        '''Get or set the generator of the feed which identifies the software
        used to generate the feed, for debugging and other purposes. Both the
        uri and version attributes are optional and only available in the ATOM
        feed.

        :param generator: Software used to create the feed.
        :param version: Version of the software.
        :param uri: URI the software can be found.
        '''
        if generator is not None:
            self.__atom_generator = {'value': generator}
            if version is not None:
                self.__atom_generator['version'] = version
            if uri is not None:
                self.__atom_generator['uri'] = uri
            self.__rss_generator = generator
        return self.__atom_generator

    def icon(self, icon=None):
        '''Get or set the icon of the feed which is a small image which
        provides iconic visual identification for the feed. Icons should be
        square. This is an ATOM only value.

        :param icon: URI of the feeds icon.
        :returns: URI of the feeds icon.
        '''
        if icon is not None:
            self.__atom_icon = icon
        return self.__atom_icon

    def logo(self, logo=None):
        '''Get or set the logo of the feed which is a larger image which
        provides visual identification for the feed. Images should be twice as
        wide as they are tall. This is an ATOM value but will also set the
        rss:image value.

        :param logo: Logo of the feed.
        :returns: Logo of the feed.
        '''
        if logo is not None:
            self.__atom_logo = logo
            self.__rss_image = {'url': logo}
        return self.__atom_logo

    def image(self, url=None, title=None, link=None, width=None, height=None,
              description=None):
        '''Set the image of the feed. This element is roughly equivalent to
        atom:logo.

        :param url: The URL of a GIF, JPEG or PNG image.
        :param title: Describes the image. The default value is the feeds
                      title.
        :param link: URL of the site the image will link to. The default is to
                     use the feeds first altertate link.
        :param width: Width of the image in pixel. The maximum is 144.
        :param height: The height of the image. The maximum is 400.
        :param description: Title of the link.
        :returns: Data of the image as dictionary.
        '''
        if url is not None:
            self.__rss_image = {'url': url}
            if title is not None:
                self.__rss_image['title'] = title
            if link is not None:
                self.__rss_image['link'] = link
            if width:
                self.__rss_image['width'] = width
            if height:
                self.__rss_image['height'] = height
            self.__atom_logo = url
        return self.__rss_image

    def rights(self, rights=None):
        '''Get or set the rights value of the feed which conveys information
        about rights, e.g. copyrights, held in and over the feed. This ATOM
        value will also set rss:copyright.

        :param rights: Rights information of the feed.
        '''
        if rights is not None:
            self.__atom_rights = rights
            self.__rss_copyright = rights
        return self.__atom_rights

    def copyright(self, copyright=None):
        '''Get or set the copyright notice for content in the channel. This RSS
        value will also set the atom:rights value.

        :param copyright: The copyright notice.
        :returns: The copyright notice.
        '''
        return self.rights(copyright)

    def subtitle(self, subtitle=None):
        '''Get or set the subtitle value of the cannel which contains a
        human-readable description or subtitle for the feed. This ATOM property
        will also set the value for rss:description.

        :param subtitle: The subtitle of the feed.
        :returns: The subtitle of the feed.
        '''
        if subtitle is not None:
            self.__atom_subtitle = subtitle
            self.__rss_description = subtitle
        return self.__atom_subtitle

    def description(self, description=None):
        '''Set and get the description of the feed. This is an RSS only element
        which is a phrase or sentence describing the channel. It is mandatory
        for RSS feeds. It is roughly the same as atom:subtitle. Thus setting
        this will also set atom:subtitle.

        :param description: Description of the channel.
        :returns: Description of the channel.

        '''
        return self.subtitle(description)

    def docs(self, docs=None):
        '''Get or set the docs value of the feed. This is an RSS only value. It
        is a URL that points to the documentation for the format used in the
        RSS file. It is probably a pointer to [1]. It is for people who might
        stumble across an RSS file on a Web server 25 years from now and wonder
        what it is.

        [1]: http://www.rssboard.org/rss-specification

        :param docs: URL of the format documentation.
        :returns: URL of the format documentation.
        '''
        if docs is not None:
            self.__rss_docs = docs
        return self.__rss_docs

    def language(self, language=None):
        '''Get or set the language of the feed. It indicates the language the
        channel is written in. This allows aggregators to group all Italian
        language sites, for example, on a single page. This is an RSS only
        field.  However, this value will also be used to set the xml:lang
        property of the ATOM feed node.
        The value should be an IETF language tag.

        :param language: Language of the feed.
        :returns: Language of the feed.
        '''
        if language is not None:
            self.__rss_language = language
            self.__atom_feed_xml_lang = language
        return self.__rss_language

    def managingEditor(self, managingEditor=None):
        '''Set or get the value for managingEditor which is the email address
        for person responsible for editorial content.    This is a RSS only
        value.

        :param managingEditor: Email address of the managing editor.
        :returns: Email address of the managing editor.
        '''
        if managingEditor is not None:
            self.__rss_managingEditor = managingEditor
        return self.__rss_managingEditor

    def pubDate(self, pubDate=None):
        '''Set or get the publication date for the content in the channel. For
        example, the New York Times publishes on a daily basis, the publication
        date flips once every 24 hours. That's when the pubDate of the channel
        changes.

        The value can either be a string which will automatically be parsed or
        a datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        This will set both atom:updated and rss:lastBuildDate.

        :param pubDate: The publication date.
        :returns: Publication date as datetime.datetime
        '''
        if pubDate is not None:
            if isinstance(pubDate, string_types):
                pubDate = dateutil.parser.parse(pubDate)
            if not isinstance(pubDate, datetime):
                raise ValueError('Invalid datetime format')
            if pubDate.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__rss_pubDate = pubDate

        return self.__rss_pubDate

    def rating(self, rating=None):
        '''Set and get the PICS rating for the channel.    It is an RSS only
        value.
        '''
        if rating is not None:
            self.__rss_rating = rating
        return self.__rss_rating

    def skipHours(self, hours=None, replace=False):
        '''Set or get the value of skipHours, a hint for aggregators telling
        them which hours they can skip. This is an RSS only value.

        This method can be called with an hour or a list of hours. The hours
        are represented as integer values from 0 to 23.

        :param hours: List of hours the feedreaders should not check the feed.
        :param replace: Add or replace old data.
        :returns: List of hours the feedreaders should not check the feed.
        '''
        if hours is not None:
            if not (isinstance(hours, list) or isinstance(hours, set)):
                hours = [hours]
            for h in hours:
                if h not in range(24):
                    raise ValueError('Invalid hour %s' % h)
            if replace or not self.__rss_skipHours:
                self.__rss_skipHours = set()
            self.__rss_skipHours |= set(hours)
        return self.__rss_skipHours

    def skipDays(self, days=None, replace=False):
        '''Set or get the value of skipDays, a hint for aggregators telling
        them which days they can skip This is an RSS only value.

        This method can be called with a day name or a list of day names. The
        days are represented as strings from 'Monday' to 'Sunday'.

        :param hours:   List of days the feedreaders should not check the feed.
        :param replace: Add or replace old data.
        :returns:       List of days the feedreaders should not check the feed.
        '''
        if days is not None:
            if not (isinstance(days, list) or isinstance(days, set)):
                days = [days]
            for d in days:
                if d not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                             'Friday', 'Saturday', 'Sunday']:
                    raise ValueError('Invalid day %s' % d)
            if replace or not self.__rss_skipDays:
                self.__rss_skipDays = set()
            self.__rss_skipDays |= set(days)
        return self.__rss_skipDays

    def textInput(self, title=None, description=None, name=None, link=None):
        '''Get or set the value of textInput. This is an RSS only field.  The
        purpose of the <textInput> element is something of a mystery. You can
        use it to specify a search engine box. Or to allow a reader to provide
        feedback. Most aggregators ignore it.

        :param title: The label of the Submit button in the text input area.
        :param description: Explains the text input area.
        :param name: The name of the text object in the text input area.
        :param link: The URL of the CGI script that processes text input
                     requests.
        :returns: Dictionary containing textInput values.
        '''
        if title is not None:
            self.__rss_textInput = {}
            self.__rss_textInput['title'] = title
            self.__rss_textInput['description'] = description
            self.__rss_textInput['name'] = name
            self.__rss_textInput['link'] = link
        return self.__rss_textInput

    def ttl(self, ttl=None):
        '''Get or set the ttl value. It is an RSS only element. ttl stands for
        time to live. It's a number of minutes that indicates how long a
        channel can be cached before refreshing from the source.

        :param ttl: Integer value indicating how long the channel may be
                    cached.
        :returns: Time to live.
        '''
        if ttl is not None:
            self.__rss_ttl = int(ttl)
        return self.__rss_ttl

    def webMaster(self, webMaster=None):
        '''Get and set the value of webMaster, which represents the email
        address for the person responsible for technical issues relating to the
        feed.  This is an RSS only value.

        :param webMaster: Email address of the webmaster.
        :returns: Email address of the webmaster.
        '''
        if webMaster is not None:
            self.__rss_webMaster = webMaster
        return self.__rss_webMaster

    def add_entry(self, feedEntry=None, order='prepend'):
        '''This method will add a new entry to the feed. If the feedEntry
        argument is omittet a new Entry object is created automatically. This
        is the preferred way to add new entries to a feed.

        :param feedEntry: FeedEntry object to add.
        :param order: If `prepend` is chosen, the entry will be inserted
                      at the beginning of the feed. If `append` is chosen,
                      the entry will be appended to the feed.
                      (default: `prepend`).
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
        for extname, ext in items:
            try:
                feedEntry.register_extension(extname,
                                             ext['extension_class_entry'],
                                             ext['atom'],
                                             ext['rss'])
            except ImportError:
                pass

        if order == 'prepend':
            self.__feed_entries.insert(0, feedEntry)
        else:
            self.__feed_entries.append(feedEntry)
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
        if entry is not None:
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
                for extname, ext in items:
                    try:
                        e.register_extension(extname,
                                             ext['extension_class_entry'],
                                             ext['atom'], ext['rss'])
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

    def load_extension(self, name, atom=True, rss=True):
        '''Load a specific extension by name.

        :param name: Name of the extension to load.
        :param atom: If the extension should be used for ATOM feeds.
        :param rss: If the extension should be used for RSS feeds.
        '''
        # Check loaded extensions
        if not isinstance(self.__extensions, dict):
            self.__extensions = {}
        if name in self.__extensions.keys():
            raise ImportError('Extension already loaded')

        # Load extension
        extname = name[0].upper() + name[1:]
        feedsupmod = __import__('feedgen.ext.%s' % name)
        feedextmod = getattr(feedsupmod.ext, name)
        try:
            entrysupmod = __import__('feedgen.ext.%s_entry' % name)
            entryextmod = getattr(entrysupmod.ext, name + '_entry')
        except ImportError:
            # Use FeedExtension module instead
            entrysupmod = feedsupmod
            entryextmod = feedextmod
        feedext = getattr(feedextmod, extname + 'Extension')
        try:
            entryext = getattr(entryextmod, extname + 'EntryExtension')
        except AttributeError:
            entryext = None
        self.register_extension(name, feedext, entryext, atom, rss)

    def register_extension(self, namespace, extension_class_feed=None,
                           extension_class_entry=None, atom=True, rss=True):
        '''Registers an extension by class.

        :param namespace: namespace for the extension
        :param extension_class_feed: Class of the feed extension to load.
        :param extension_class_entry: Class of the entry extension to load
        :param atom: If the extension should be used for ATOM feeds.
        :param rss: If the extension should be used for RSS feeds.
        '''
        # Check loaded extensions
        # `load_extension` ignores the "Extension" suffix.
        if not isinstance(self.__extensions, dict):
            self.__extensions = {}
        if namespace in self.__extensions.keys():
            raise ImportError('Extension already loaded')

        # Load extension
        extinst = extension_class_feed()
        setattr(self, namespace, extinst)

        # `load_extension` registry
        self.__extensions[namespace] = {
                'inst': extinst,
                'extension_class_feed': extension_class_feed,
                'extension_class_entry': extension_class_entry,
                'atom': atom,
                'rss': rss
                }

        # Try to load the extension for already existing entries:
        for entry in self.__feed_entries:
            try:
                entry.register_extension(namespace,
                                         extension_class_entry,
                                         atom,
                                         rss)
            except ImportError:
                pass
