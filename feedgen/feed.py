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
from feedgen.util import ensure_format
import feedgen.version


_feedgen_version = feedgen.version.version_str


class FeedGenerator(object):
	'''FeedGenerator for generating ATOM and RSS feeds.
	'''


	def __init__(self):
		self.__extensions = {}
		self.__feed_entries = []

		## ATOM
		# http://www.atomenabled.org/developers/syndication/
		# required
		self.__atom_id      = None
		self.__atom_title   = None
		self.__atom_updated = datetime.now(dateutil.tz.tzutc())

		# recommended
		self.__atom_author = None # {name*, uri, email}
		self.__atom_link   = None # {href*, rel, type, hreflang, title, length}

		# optional
		self.__atom_category    = None # {term*, schema, label}
		self.__atom_contributor = None
		self.__atom_generator   = {
				'value'  :'python-feedgen',
				'url'    :'http://lkiesow.github.io/python-feedgen',
				'version':feedgen.version.version_str } #{value*,uri,version}
		self.__atom_icon     = None
		self.__atom_logo     = None
		self.__atom_rights   = None
		self.__atom_subtitle = None

		# other
		self.__atom_feed_xml_lang = None

		## RSS
		# http://www.rssboard.org/rss-specification
		self.__rss_title       = None
		self.__rss_link        = None
		self.__rss_description = None

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

		# Extension list:
		__extensions = {}


	def _create_atom(self, extensions=True):
		'''Create a ATOM feed xml structure containing all previously set fields.

		:returns: Tuple containing the feed root element and the element tree.
		'''
		feed    = etree.Element('feed',  xmlns='http://www.w3.org/2005/Atom')
		if self.__atom_feed_xml_lang:
			feed.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = \
					self.__atom_feed_xml_lang

		if not ( self.__atom_id and self.__atom_title and self.__atom_updated ):
			missing = ', '.join(([] if self.__atom_title else ['title']) + \
					([] if self.__atom_id else ['id']) + \
					([] if self.__atom_updated else ['updated']))
			raise ValueError('Required fields not set (%s)' % missing)
		id      = etree.SubElement(feed, 'id')
		id.text = self.__atom_id
		title   = etree.SubElement(feed, 'title')
		title.text = self.__atom_title
		updated   = etree.SubElement(feed, 'updated')
		updated.text = self.__atom_updated.isoformat()

		# Add author elements
		for a in self.__atom_author or []:
			# Atom requires a name. Skip elements without.
			if not a.get('name'):
				continue
			author = etree.SubElement(feed, 'author')
			name = etree.SubElement(author, 'name')
			name.text = a.get('name')
			if a.get('email'):
				email = etree.SubElement(author, 'email')
				email.text = a.get('email')
			if a.get('uri'):
				email = etree.SubElement(author, 'url')
				email.text = a.get('uri')

		for l in self.__atom_link or []:
			link = etree.SubElement(feed, 'link', href=l['href'])
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
			cat = etree.SubElement(feed, 'category', term=c['term'])
			if c.get('schema'):
				cat.attrib['schema'] = c['schema']
			if c.get('label'):
				cat.attrib['label'] = c['label']

		# Add author elements
		for c in self.__atom_contributor or []:
			# Atom requires a name. Skip elements without.
			if not c.get('name'):
				continue
			contrib = etree.SubElement(feed, 'contributor')
			name = etree.SubElement(contrib, 'name')
			name.text = c.get('name')
			if c.get('email'):
				email = etree.SubElement(contrib, 'email')
				email.text = c.get('email')
			if c.get('uri'):
				email = etree.SubElement(contrib, 'url')
				email.text = c.get('uri')

		if self.__atom_generator:
			generator = etree.SubElement(feed, 'generator')
			generator.text = self.__atom_generator['value']
			if self.__atom_generator.get('uri'):
				generator.attrib['uri'] = self.__atom_generator['uri']
			if self.__atom_generator.get('version'):
				generator.attrib['version'] = self.__atom_generator['version']

		if self.__atom_icon:
			icon = etree.SubElement(feed, 'icon')
			icon.text = self.__atom_icon

		if self.__atom_logo:
			logo = etree.SubElement(feed, 'logo')
			logo.text = self.__atom_logo

		if self.__atom_rights:
			rights = etree.SubElement(feed, 'rights')
			rights.text = self.__atom_rights

		if self.__atom_subtitle:
			subtitle = etree.SubElement(feed, 'subtitle')
			subtitle.text = self.__atom_subtitle

		if extensions:
			for ext in self.__extensions.values() or []:
				if ext.get('atom'):
					feed = ext['inst'].extend_atom(feed)

		for entry in self.__feed_entries:
			entry.atom_entry(feed)

		doc = etree.ElementTree(feed)
		return feed, doc


	def atom_str(self, pretty=False, extensions=True):
		'''Generates an ATOM feed and returns the feed XML as string.
		
		:param pretty: If the feed should be split into multiple lines and
			properly indented.
		:param extensions: Enable or disable the loaded extensions for the xml
			generation (default: enabled).
		:returns: String representation of the ATOM feed.
		'''
		feed, doc = self._create_atom(extensions=extensions)
		return etree.tostring(feed, pretty_print=pretty)


	def atom_file(self, filename, extensions=True):
		'''Generates an ATOM feed and write the resulting XML to a file.
		
		:param filename: Name of file to write.
		:param extensions: Enable or disable the loaded extensions for the xml
			generation (default: enabled).
		'''
		feed, doc = self._create_atom(extensions=extensions)
		with open(filename, 'w') as f:
			doc.write(f)


	def _create_rss(self, extensions=True):
		'''Create an RSS feed xml structure containing all previously set fields.

		:returns: Tuple containing the feed root element and the element tree.
		'''
		feed    = etree.Element('rss', version='2.0',
				nsmap={'atom':  'http://www.w3.org/2005/Atom'} )
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
		for ln in  self.__atom_link or []:
			# It is recommended to include a atom self link in rss documents…
			if ln.get('rel') == 'self':
				selflink = etree.SubElement(channel, 
						'{http://www.w3.org/2005/Atom}link', 
						href=ln['href'], rel='self')
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
			lastBuildDate.text = self.__rss_lastBuildDate.strftime(
					'%a, %d %b %Y %H:%M:%S %z')
		if self.__rss_managingEditor:
			managingEditor = etree.SubElement(channel, 'managingEditor')
			managingEditor.text = self.__rss_managingEditor
		if self.__rss_pubDate:
			pubDate = etree.SubElement(channel, 'pubDate')
			pubDate.text = self.__rss_pubDate.strftime(
					'%a, %d %b %Y %H:%M:%S %z')
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
			ttl.text = self.__rss_ttl
		if self.__rss_webMaster:
			webMaster = etree.SubElement(channel, 'webMaster')
			webMaster.text = self.__rss_webMaster

		if extensions:
			for ext in self.__extensions.values() or []:
				if ext.get('rss'):
					feed = ext['inst'].extend_rss(feed)

		for entry in self.__feed_entries:
			entry.rss_entry(channel)

		doc = etree.ElementTree(feed)
		return feed, doc


	def rss_str(self, pretty=False, extensions=True):
		'''Generates an RSS feed and returns the feed XML as string.
		
		:param pretty: If the feed should be split into multiple lines and
			properly indented.
		:param extensions: Enable or disable the loaded extensions for the xml
			generation (default: enabled).
		:returns: String representation of the RSS feed.
		'''
		feed, doc = self._create_rss(extensions=extensions)
		return etree.tostring(feed, pretty_print=pretty)


	def rss_file(self, filename, extensions=True):
		'''Generates an RSS feed and write the resulting XML to a file.
		
		:param filename: Name of file to write.
		:param extensions: Enable or disable the loaded extensions for the xml
			generation (default: enabled).
		'''
		feed, doc = self._create_rss(extensions=extensions)
		with open(filename, 'w') as f:
			doc.write(f)

	
	def title(self, title=None):
		'''Get or set the title value of the feed. It should contain a human
		readable title for the feed. Often the same as the title of the
		associated website. Title is mandatory for both ATOM and RSS and should
		not be blank.

		:param title: The new title of the feed.
		:returns: The feeds title.
		'''
		if not title is None:
			self.__atom_title = title
			self.__rss_title = title
			print 'rss-title: ', self.__rss_title
		return self.__atom_title


	def id(self, id=None):
		'''Get or set the feed id which identifies the feed using a universally
		unique and permanent URI. If you have a long-term, renewable lease on
		your Internet domain name, then you can feel free to use your website's
		address. This field is for ATOM only. It is mandatory for ATOM.

		:param id: New Id of the ATOM feed.
		:returns: Id of the feed.
		'''
		
		if not id is None:
			self.__atom_id = id
		return self.__atom_id


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
		:returns: Modification date as datetime.datetime
		'''
		if not updated is None:
			if isinstance(updated, basestring):
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

		The value can either be a string which will automatically be parsed or a
		datetime.datetime object. In any case it is necessary that the value
		include timezone information.

		This will set both atom:updated and rss:lastBuildDate.

		Default value
			If not set, lastBuildDate has as value the current date and time.

		:param lastBuildDate: The modification date.
		:returns: Modification date as datetime.datetime
		'''
		return updated( lastBuildDate )


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
			if replace or self.__atom_author is None:
				self.__atom_author = []
			self.__atom_author += ensure_format( author, 
					set(['name', 'email', 'uri']), set(['name']))
			self.__rss_author = []
			for a in self.__atom_author:
				if a.get('email'):
					self.__rss_author.append(a['email'])
		return self.__atom_author


	def link(self, link=None, replace=False, **kwargs):
		'''Get or set link data. An link element is a dict with the fields href,
		rel, type, hreflang, title, and length. Href is mandatory for ATOM.

		This method can be called with:
		- the fields of a link as keyword arguments
		- the fields of a link as a dictionary
		- a list of dictionaries containing the link fields

		A link has the following fields:

		- *href* is the URI of the referenced resource (typically a Web page)
		- *rel* contains a single link relationship type. It can be a full URI,
		  or one of the following predefined values (default=alternate):

			- *alternate* an alternate representation of the entry or feed, for
			  example a permalink to the html version of the entry, or the front
			  page of the weblog.
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
		:param replace: Add or replace old data.

		Example::

			>>> feedgen.link( href='http://example.com/', rel='self')
			[{'href':'http://example.com/', 'rel':'self'}]

		'''
		if link is None and kwargs:
			link = kwargs
		if not link is None:
			if replace or self.__atom_link is None:
				self.__atom_link = []
			self.__atom_link += ensure_format( link, 
					set(['href', 'rel', 'type', 'hreflang', 'title', 'length']),
					set(['href']), 
					{'rel':['alternate', 'enclosure', 'related', 'self', 'via']} )
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

		If a label is present it is used for the RSS feeds. Otherwise the term is
		used. The scheme is used for the domain attribute in RSS.

		:param link:    Dict or list of dicts with data.
		:param replace: Add or replace old data.
		:returns: List of category data.
		'''
		if category is None and kwargs:
			category = kwargs
		if not category is None:
			if replace or self.__atom_category is None:
				self.__atom_category = []
			self.__atom_category += ensure_format( 
					category, 
					set(['term', 'scheme', 'label']),
					set(['term']) )
			# Map the ATOM categories to RSS categories. Use the atom:label as
			# name or if not present the atom:term. The atom:schema is the
			# rss:domain.
			self.__rss_category = []
			for cat in self.__atom_category:
				rss_cat = {}
				rss_cat['value'] = cat['label'] if cat.get('label') else cat['term']
				if cat.get('schema'):
					rss_cat['domain'] = cat['schema']
				self.__rss_category.append( rss_cat )
		return self.__atom_category


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
			self.__rss_cloud = {'donain':domain, 'port':port, 'path':path,
					'registerProcedure':registerProcedure, 'protocol':protocol}
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
		
		:param contributor: Dictionary or list of dictionaries with contributor data.
		:param replace: Add or replace old data.
		:returns: List of contributors as dictionaries.
		'''
		if contributor is None and kwargs:
			contributor = kwargs
		if not contributor is None:
			if replace or self.__atom_contributor is None:
				self.__atom_contributor = []
			self.__atom_contributor += ensure_format( contributor, 
					set(['name', 'email', 'uri']), set(['name']))
		return self.__atom_contributor


	def generator(self, generator=None, version=None, uri=None):
		'''Get or the generator of the feed which identifies the software used to
		generate the feed, for debugging and other purposes. Both the uri and
		version attributes are optional and only available in the ATOM feed.

		:param generator: Software used to create the feed.
		:param version: Version of the software.
		:param uri: URI the software can be found.
		'''
		if not generator is None:
			self.__atom_generator = {'value':generator}
			if not version in None:
				self.__atom_generator['version'] = version
			if not uri in None:
				self.__atom_generator['uri'] = uri
			self.__rss_generator = generator
		return self.__atom_generator


	def icon(self, icon=None):
		'''Get or set the icon of the feed which is a small image which provides
		iconic visual identification for the feed. Icons should be square. This
		is an ATOM only value.

		:param icon: URI of the feeds icon.
		:returns: URI of the feeds icon.
		'''
		if not icon is None:
			self.__atom_icon = icon
		return self.__atom_icon


	def logo(self, logo=None):
		'''Get or set the logo of the feed which is a larger image which provides
		visual identification for the feed. Images should be twice as wide as
		they are tall. This is an ATOM value but will also set the rss:image
		value.

		:param logo: Logo of the feed.
		:returns: Logo of the feed.
		'''
		if not logo is None:
			self.__atom_logo = logo
			self.__rss_image = { 'url' : logo }
		return self.__atom_logo


	def image(self, url=None, title=None, link=None, width=None, height=None,
			description=None):
		'''Set the image of the feed. This element is roughly equivalent to
		atom:logo.

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
			self.__atom_logo = url
		return self.__rss_image


	def rights(self, rights=None):
		'''Get or set the rights value of the feed which conveys information
		about rights, e.g. copyrights, held in and over the feed. This ATOM value
		will also set rss:copyright.

		:param rights: Rights information of the feed.
		'''
		if not rights is None:
			self.__atom_rights = rights
			self.__rss_copyright = rights
		return self.__atom_rights


	def copyright(self, copyright=None):
		'''Get or set the copyright notice for content in the channel. This RSS
		value will also set the atom:rights value.

		:param copyright: The copyright notice.
		:returns: The copyright notice.
		'''
		return rights( copyright )


	def subtitle(self, subtitle=None):
		'''Get or set the subtitle value of the cannel which contains a
		human-readable description or subtitle for the feed. This ATOM property
		will also set the value for rss:description.

		:param subtitle: The subtitle of the feed.
		:returns: The subtitle of the feed.
		'''
		if not subtitle is None:
			self.__atom_subtitle   = subtitle
			self.__rss_description = subtitle
		return self.__atom_subtitle


	def description(self, description=None):
		'''Set and get the description of the feed. This is an RSS only element
		which is a phrase or sentence describing the channel. It is mandatory for
		RSS feeds. It is roughly the same as atom:subtitle. Thus setting this
		will also set atom:subtitle.

		:param description: Description of the channel.
		:returns: Description of the channel.

		'''
		return self.subtitle( description )


	def docs(self, docs=None):
		'''Get or set the docs value of the feed. This is an RSS only value. It
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
		language sites, for example, on a single page. This is an RSS only field.
		However, this value will also be used to set the xml:lang property of the
		ATOM feed node.
		The value should be an IETF language tag.

		:param language: Language of the feed.
		:returns: Language of the feed.
		'''
		if not language is None:
			self.__rss_language = language
			self.__atom_feed_xml_lang = language
		return self.__rss_language


	def managingEditor(self, managingEditor=None):
		'''Set or get the value for managingEditor which is the email address for
		person responsible for editorial content.	This is a RSS only value.

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

		This will set both atom:updated and rss:lastBuildDate.

		:param pubDate: The publication date.
		:returns: Publication date as datetime.datetime
		'''
		if not pubDate is None:
			if isinstance(pubDate, basestring):
				pubDate = dateutil.parser.parse(pubDate)
			if not isinstance(pubDate, datetime):
				raise ValueError('Invalid datetime format')
			if pubDate.tzinfo is None:
				raise ValueError('Datetime object has no timezone info')
			self.__rss_pubDate = pubDate

		return self.__rss_pubDate


	def rating(self, rating=None):
		'''Set and get the PICS rating for the channel.	It is an RSS only
		value.
		'''
		if not rating is None:
			self.__rss_rating = rating
		return self.__rss_rating


	def skipHours(self, hours=None, replace=False):
		'''Set or get the value of skipHours, a hint for aggregators telling them
		which hours they can skip. This is an RSS only value.

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
				if not h in xrange(24):
					raise ValueError('Invalid hour %s' % h)
			if replace or not self.__rss_skipHours:
				self.__rss_skipHours = set()
			self.__rss_skipHours |= set(hours)
		return self.__rss_skipHours


	def skipDays(self, days=None, replace=False):
		'''Set or get the value of skipDays, a hint for aggregators telling them
		which days they can skip This is an RSS only value.

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
					raise ValueError('Invalid day %s' % h)
			if replace or not self.__rss_skipDays:
				self.__rss_skipDays = set()
			self.__rss_skipDays |= set(days)
		return self.__rss_skipDays


	def textInput(self, title=None, description=None, name=None, link=None):
		'''Get or set the value of textInput. This is an RSS only field.  The
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
		'''Get or set the ttl value. It is an RSS only element. ttl stands for
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
		This is an RSS only value.

		:param webMaster: Email address of the webmaster.
		:returns: Email address of the webmaster.
		'''
		if not webMaster is None:
			self.__rss_webMaster = webMaster
		return self.__rss_webMaster


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

		# Try to load extensions:
		for extname,ext in self.__extensions.iteritems():
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


			# Try to load extensions:
			for e in entry:
				for extname,ext in self.__extensions.iteritems():
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
		extname = name[0].upper() + name[1:] + 'Extension'
		supmod = __import__('feedgen.ext.%s' % name)
		extmod = getattr(supmod.ext, name)
		ext    = getattr(extmod, extname)
		extinst = ext()
		setattr(self, name, extinst)
		self.__extensions[name] = {'inst':extinst,'atom':atom,'rss':rss}

		# Try to load the extension for already existing entries:
		for entry in self.__feed_entries:
			try:
				entry.load_extension( name, atom, rss )
			except ImportError:
				pass
