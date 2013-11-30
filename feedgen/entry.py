# -*- coding: utf-8 -*-
'''
	feedgen.entry
	~~~~~~~~~~~~~

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see license.* for more details.
'''

from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from feedgen.util import ensure_format


class FeedEntry(object):
	'''FeedEntry call representing an ATOM feeds entry node or an RSS feeds item
	node.
	'''

	def __init__(self):
		# ATOM
		# required
		self.__atom_id      = None
		self.__atom_title   = None
		self.__atom_updated = datetime.now(dateutil.tz.tzutc())

		# recommended
		self.__atom_author  = None
		self.__atom_content = None
		self.__atom_link    = None
		self.__atom_summary = None

		# optional
		self.__atom_category    = None
		self.__atom_contributor = None
		self.__atom_published   = None
		self.__atom_source      = None
		self.__atom_rights      = None

		# RSS
		self.__rss_author      = None
		self.__rss_category    = None
		self.__rss_comments    = None
		self.__rss_description = None
		self.__rss_enclosure   = None
		self.__rss_guid        = None
		self.__rss_link        = None
		self.__rss_pubDate     = None
		self.__rss_source      = None
		self.__rss_title       = None

		# Extension list:
		self.__extensions = {}


	def atom_entry(self, feed, extensions=True):
		'''Insert an ATOM entry into a existing XML structure. Normally you
		would pass the feed node of an ATOM feed XML to this function.

		:param feed: The XML element to use as parent node for the element.
		'''
		entry = etree.SubElement(feed, 'entry')
		if not ( self.__atom_id and self.__atom_title and self.__atom_updated ):
			raise ValueError('Required fields not set')
		id      = etree.SubElement(entry, 'id')
		id.text = self.__atom_id
		title   = etree.SubElement(entry, 'title')
		title.text = self.__atom_title
		updated   = etree.SubElement(entry, 'updated')
		updated.text = self.__atom_updated.isoformat()

		# An entry must contain an alternate link if there is no content element.
		if not self.__atom_content:
			if not True in [ l.get('rel') == 'alternate' \
					for l in self.__atom_link or [] ]:
				raise ValueError('Entry must contain an alternate link or '
						+ 'a content element.')

		# Add author elements
		for a in self.__atom_author or []:
			# Atom requires a name. Skip elements without.
			if not a.get('name'):
				continue
			author = etree.SubElement(entry, 'author')
			name = etree.SubElement(author, 'name')
			name.text = a.get('name')
			if a.get('email'):
				email = etree.SubElement(author, 'email')
				email.text = a.get('email')
			if a.get('uri'):
				email = etree.SubElement(author, 'url')
				email.text = a.get('uri')

		if self.__atom_content:
			content = etree.SubElement(entry, 'content')
			type = self.__atom_content.get('type')
			if self.__atom_content.get('src'):
				content.attrib['src'] = self.__atom_content['src']
			elif self.__atom_content.get('content'):
				# Surround xhtml with a div tag, parse it and embed it
				if type == 'xhtml':
					content.append(etree.fromstring('''<div
							xmlns="http://www.w3.org/1999/xhtml">%s</div>''' % \
							self.__atom_content.get('content')))
				# Emed the text in escaped form
				elif not type or type.startswith('text') or type == 'html':
					content.text = self.__atom_content.get('content')
				# Parse XML and embed it
				elif type.endswith('/xml') or type.endswith('+xml'):
					content.append(etree.fromstring(self.__atom_content['content']))
				# Everything else should be included base64 encoded
				else:
					raise ValueError('base64 encoded content is not supported at the moment.'
							+ 'If you are interested , please file a bug report.')
			# Add type description of the content
			if type:
				content.attrib['type'] = type

		for l in self.__atom_link or []:
			link = etree.SubElement(entry, 'link', href=l['href'])
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

		if self.__atom_summary:
			summary = etree.SubElement(entry, 'summary')
			summary.text = self.__atom_summary

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

		if self.__atom_published:
			published   = etree.SubElement(entry, 'published')
			published.text = self.__atom_published.isoformat()

		if self.__atom_rights:
			rights = etree.SubElement(feed, 'rights')
			rights.text = self.__atom_rights

		if extensions:
			for ext in self.__extensions.values() or []:
				if ext.get('atom'):
					entry = ext['inst'].extend_atom(entry)

		return entry


	def rss_entry(self, feed, extensions=True):
		'''Insert an RSS item into a existing XML structure. Normally you
		would pass the channel node of an RSS feed XML to this function.

		:param feed: The XML element to use as parent node for the item.
		'''
		entry = etree.SubElement(feed, 'item')
		if not ( self.__rss_title or self.__rss_description ):
			raise ValueError('Required fields not set')
		if self.__rss_title:
			title = etree.SubElement(entry, 'title')
			title.text = self.__rss_title
		if self.__rss_link:
			link = etree.SubElement(entry, 'link')
			link.text = self.__rss_link
		if self.__rss_description:
			description = etree.SubElement(entry, 'description')
			description.text = self.__rss_description
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
			pubDate.text = self.__rss_pubDate.strftime(
					'%a, %d %b %Y %H:%M:%S %z')

		if extensions:
			for ext in self.__extensions.values() or []:
				if ext.get('rss'):
					entry = ext['inst'].extend_rss(entry)

		return entry


	
	def title(self, title=None):
		'''Get or set the title value of the entry. It should contain a human
		readable title for the entry. Title is mandatory for both ATOM and RSS
		and should not be blank.

		:param title: The new title of the entry.
		:returns: The entriess title.
		'''
		if not title is None:
			self.__atom_title = title
			self.__rss_title = title
		return self.__atom_title


	def id(self, id=None):
		'''Get or set the entry id which identifies the entry using a universally
		unique and permanent URI. Two entries in a feed can have the same value
		for id if they represent the same entry at different points in time. This
		method will also set rss:guid.  Id is mandatory for an ATOM entry.

		:param id: New Id of the entry.
		:returns: Id of the entry.
		'''
		if not id is None:
			self.__atom_id = id
			self.__rss_guid = id
		return self.__atom_id


	def guid(self, guid=None):
		'''Get or set the entries guid which is a string that uniquely identifies
		the item. This will also set atom:id.

		:param guid: Id of the entry.
		:returns: Id of the entry.
		'''
		return self.id(guid)


	def updated(self, updated=None):
		'''Set or get the updated value which indicates the last time the entry
		was modified in a significant way.

		The value can either be a string which will automatically be parsed or a
		datetime.datetime object. In any case it is necessary that the value
		include timezone information.

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


	def author(self, author=None, replace=False, **kwargs):
		'''Get or set autor data. An author element is a dict containing a name,
		an email adress and a uri. Name is mandatory for ATOM, email is mandatory
		for RSS.

		This method can be called with:
		- the fields of an author as keyword arguments
		- the fields of an author as a dictionary
		- a list of dictionaries containing the author fields

		An author has the following fields:
		- *name* conveys a human-readable name for the person.
		- *uri* contains a home page for the person.
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
			if replace or self.__atom_author is None:
				self.__atom_author = []
			self.__atom_author += ensure_format( author, 
					set(['name', 'email', 'uri']), set(['name']))
			self.__rss_author = []
			for a in self.__atom_author:
				if a.get('email'):
					self.__rss_author.append('%s (%s)' % ( a['email'], a['name'] ))
		return self.__atom_author


	def content(self, content=None, src=None, type=None):
		'''Get or set the cntent of the entry which contains or links to the
		complete content of the entry. Content must be provided for ATOM entries
		if there is no alternate link, and should be provided if there is no
		summary. If the content is set (not linked) it will also set
		rss:description.

		:param content: The content of the feed entry.
		:param src: Link to the entries content.
		:returns: Content element of the entry.
		'''
		if not src is None:
			self.__atom_content = {'src':src}
		elif not content is None:
			self.__atom_content = {'content':content}
			if not type is None:
				self.__atom_content['type'] = type
			self.__rss_description = content
		return self.__atom_content


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

		RSS only supports one link with nothing but a URL. So for the RSS link
		element the last link with rel=alternate is used.

		RSS also supports one enclusure element per entry which is covered by the
		link element in ATOM feed entries. So for the RSS enclusure element the
		last link with rel=enclosure is used.
		
		:param link:    Dict or list of dicts with data.
		:param replace: Add or replace old data.
		:returns: List of link data.
		'''
		if link is None and kwargs:
			link = kwargs
		if not link is None:
			if replace or self.__atom_link is None:
				self.__atom_link = []
			self.__atom_link += ensure_format( link, 
					set(['href', 'rel', 'type', 'hreflang', 'title', 'length']),
					set(['href']), 
					{'rel':['alternate', 'enclosure', 'related', 'self', 'via']},
					{'rel': 'alternate'} )
			# RSS only needs one URL. We use the first link for RSS:
			for l in self.__atom_link:
				if l.get('rel') == 'alternate':
					self.__rss_link = l['href']
				elif l.get('rel') == 'enclosure':
					self.__rss_enclosure = {'url':l['href']}
					self.__rss_enclosure['type'] = l.get('type')
					self.__rss_enclosure['length'] = l.get('length') or '0'
		# return the set with more information (atom)
		return self.__atom_link


	def summary(self, summary=None):
		'''Get or set the summary element of an entry which conveys a short
		summary, abstract, or excerpt of the entry. Summary is an ATOM only
		element and should be provided if there either is no content provided for
		the entry, or that content is not inline (i.e., contains a src
		attribute), or if the content is encoded in base64.
		This method will also set the rss:description field if it wasn't
		previously set or contains the old value of summary.

		:param summary: Summary of the entries contents.
		:returns: Summary of the entries contents.
		'''
		if not summary is None:
			# Replace the RSS description with the summary if it was the summary
			# before. Not if is the description.
			if not self.__rss_description or \
					self.__rss_description == self.__atom_summary:
				self.__rss_description = summary
			self.__atom_summary = summary
		return self.__atom_summary


	def description(self, description=None, isSummary=False):
		'''Get or set the description value which is the item synopsis.
		Description is an RSS only element. For ATOM feeds it is split in summary
		and content. The isSummary parameter can be used to control which ATOM
		value is set when setting description.

		:param description: Description of the entry.
		:param isSummary: If the description should be used as content or summary.
		:returns: The entries description.
		'''
		if not description is None:
			self.__rss_description = description
			if isSummary:
				self.__atom_summary = description
			else:
				self.__atom_content = description
		return self.__rss_description


	def category(self, category=None, replace=False, **kwargs):
		'''Get or set categories that the entry belongs to.

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
			if isinstance(published, basestring):
				published = dateutil.parser.parse(published)
			if not isinstance(published, datetime):
				raise ValueError('Invalid datetime format')
			if published.tzinfo is None:
				raise ValueError('Datetime object has no timezone info')
			self.__atom_published = published
			self.__rss_pubDate = published

		return self.__atom_published

	
	def pubdate(self, pubDate=None):
		'''Get or set the pubDate of the entry which indicates when the entry was
		published. This method is just another name for the published(...)
		method.
		'''
		return self.published(pubDate)


	def rights(self, rights=None):
		'''Get or set the rights value of the entry which conveys information
		about rights, e.g. copyrights, held in and over the entry. This ATOM value
		will also set rss:copyright.

		:param rights: Rights information of the feed.
		:returns: Rights information of the feed.
		'''
		if not rights is None:
			self.__atom_rights = rights
		return self.__atom_rights


	def comments(self, comments=None):
		'''Get or set the the value of comments which is the url of the comments
		page for the item. This is a RSS only value.

		:param comments: URL to the comments page.
		:returns: URL to the comments page.
		'''
		if not comments is None:
			self.__rss_comments = comments
		return self.__rss_comments


	def enclosure(self, url=None, length=None, type=None):
		'''Get or set the value of enclosure which describes a media object that
		is attached to the item. This is a RSS only value which is represented by
		link(rel=enclosure) in ATOM. ATOM feeds can furthermore contain several
		enclosures while RSS may contain only one. That is why this method, if
		repeatedly called, will add more than one enclosures to the feed.
		However, only the last one is used for RSS.

		:param url: URL of the media object.
		:param length: Size of the media in bytes.
		:param type: Mimetype of the linked media.
		:returns: Data of the enclosure element.
		'''
		if not url is None:
			self.link( href=url, rel='enclosure', type=type, length=length )
		return self.__rss_enclosure


	def ttl(self, ttl=None):
		'''Get or set the ttl value. It is an RSS only element. ttl stands for
		time to live. It's a number of minutes that indicates how long a channel
		can be cached before refreshing from the source.

		:param ttl: Integer value representing the time to live.
		:returns: Time to live of of the entry.
		'''
		if not ttl is None:
			self.__rss_ttl = int(ttl)
		return self.__rss_ttl

	
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
		self.__extensions[name] = {'inst':extinst,'atom':atom,'rss':rss}
