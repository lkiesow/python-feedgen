#!/bin/env python
# -*- coding: utf-8 -*-
'''
	feedgenerator
	~~~~~~~~~~~~~

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see LICENSE for more details.
'''

from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz


class FeedGenerator:

	__feed_entries = []

	## ATOM
	# http://www.atomenabled.org/developers/syndication/
	# required
	__atom_id = None
	__atom_title = None
	__atom_updated = datetime.now(dateutil.tz.tzutc())

	# recommended
	__atom_author = None # {name*, uri, email}
	__atom_link = None # {href*, rel, type, hreflang, title, length}

	# optional
	__atom_category = None # {term*, schema, label}
	__atom_contributor = None
	__atom_generator = {'value':'Lernfunk3 FeedGenerator'} #{value*,uri,version}
	__atom_icon = None
	__atom_logo = None
	__atom_rights = None
	__atom_subtitle = None

	# other
	__atom_feed_xml_lang = None

	## RSS
	# http://www.rssboard.org/rss-specification
	__rss_title = None
	__rss_link = None
	__rss_description = None

	__rss_category       = None
	__rss_cloud          = None
	__rss_copyright      = None
	__rss_docs           = 'http://www.rssboard.org/rss-specification'
	__rss_generator      = 'Lernfunk3 FeedGenerator'
	__rss_image          = None
	__rss_language       = None
	__rss_lastBuildDate  = datetime.now(dateutil.tz.tzutc())
	__rss_managingEditor = None
	__rss_pubDate        = None
	__rss_rating         = None
	__rss_skipHours      = None
	__rss_skipDays       = None
	__rss_textInput      = None
	__rss_ttl            = None
	__rss_webMaster      = None



	def __ensure_format(self, val, allowed, required, allowed_values={}):
		if not val:
			return None
		# Make shure that we have a list of dicts. Even if there is only one.
		if not isinstance(val, list):
			val = [val]
		for elem in val:
			if not isinstance(elem, dict):
				raise ValueError('Invalid data (value is no dictionary)')
			if not set(elem.keys()) <= allowed:
				raise ValueError('Data contains invalid keys')
			if not set(elem.keys()) >= required:
				raise ValueError('Data contains not all required keys')
			for k,v in allowed_values.iteritems():
				if elem.get(k) and not elem[k] in v:
					raise ValueError('Invalid value for %s' % k )
		return val


	def __create_atom(self):
		feed    = etree.Element('feed',  xmlns='http://www.w3.org/2005/Atom')
		if self.__atom_feed_xml_lang:
			feed.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = \
					self.__atom_feed_xml_lang

		doc     = etree.ElementTree(feed)
		if not ( self.__atom_id and self.__atom_title and self.__atom_updated ):
			raise ValueError('Required fields not set')
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

		for entry in self.__feed_entries:
			entry.atom_entry(feed)

		return feed, doc


	def atom_str(self, pretty=False):
		feed, doc = self.__create_atom()
		return etree.tostring(feed, pretty_print=pretty)


	def atom_file(self, filename):
		feed, doc = self.__create_atom()
		with open(filename, 'w') as f:
			doc.write(f)


	def __create_rss(self):
		feed    = etree.Element('rss', version='2.0')
		doc     = etree.ElementTree(feed)
		channel = etree.SubElement(feed, 'channel')
		if not ( self.__rss_title and self.__rss_link and self.__rss_description ):
			raise ValueError('Required fields not set')
		title = etree.SubElement(channel, 'title')
		title.text = self.__rss_title
		link = etree.SubElement(channel, 'link')
		link.text = self.__rss_link
		link = etree.SubElement(channel, 'description')
		link.text = self.__rss_description
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
			image.attrib['url'] = self.__rss_image.get('url')
			image.attrib['title'] = self.__rss_image['title'] \
					if self.__rss_image.get('title') else self.__rss_title
			image.attrib['link'] = self.__rss_image['link'] \
					if self.__rss_image.get('link') else self.__rss_link
			if self.__rss_image.get('width'):
				image.attrib['width'] = self.__rss_image.get('width')
			if self.__rss_image.get('height'):
				image.attrib['height'] = self.__rss_image.get('height')
			if self.__rss_image.get('description'):
				image.attrib['description'] = self.__rss_image.get('description')
		if self.__rss_language:
			language = etree.SubElement(channel, 'language')
			language.text = self.__rss_language
		if self.__rss_lastBuildDate:
			lastBuildDate = etree.SubElement(channel, 'lastBuildDate')
			lastBuildDate.text = self.__rss_lastBuildDate.strftime(
					'%a, %e %b %Y %H:%M:%S %z')
		if self.__rss_managingEditor:
			managingEditor = etree.SubElement(channel, 'managingEditor')
			managingEditor.text = self.__rss_managingEditor
		if self.__rss_pubDate:
			pubDate = etree.SubElement(channel, 'pubDate')
			pubDate.text = self.__rss_pubDate.strftime(
					'%a, %e %b %Y %H:%M:%S %z')
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

		return feed, doc


	def rss_str(self, pretty=False):
		feed, doc = self.__create_rss()
		return etree.tostring(feed, pretty_print=pretty)


	def rss_file(self, filename):
		feed, doc = self.__create_rss()
		with open(filename, 'w') as f:
			doc.write(f)

	
	def title(self, title=None):
		if not title is None:
			self.__atom_title = title
			self.__rss_title = title
		return self.__atom_title


	def id(self, id=None):
		if not id is None:
			self.__atom_id = id
		return self.__atom_id


	def updated(self, updated=None):
		'''Set or get the updated value which indicates the last time the feed
		was modified in a significant way.

		The value can either be a string which will automatically be parsed or a
		datetime.datetime object. In any case it is necessary that the value
		include timezone information.

		:param updated: The modification date.
		:returns: Modification date as datetime.datetime
		'''
		if not updated is None:
			if isinstance(updated, basestr):
				updated = dateutil.parser.parse(updated)
			if not isinstance(updated, datetime.datetime):
				ValueError('Invalid datetime format')
			if updated.tzinfo is None:
				ValueError('Datetime object has no timezone info')
			self.__atom_updated = updated
			self.__rss_lastBuildDate = updated

		return self.__atom_updated


	def lastBuildDate(self, lastBuildDate=None):
		return updated( lastBuildDate )


	def author(self, author=None, replace=False, **kwargs):
		'''Get or set autor data. An author element is a dict containing a name,
		an email adress and a uri. Name is mandatory for ATOM, email is mandatory
		for RSS.
		
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
			self.__atom_author += self.__ensure_format( author, 
					set(['name', 'email', 'uri']), set(['name']))
		return self.__atom_author


	def link(self, link=None, replace=False, **kwargs):
		'''Get or set link data. An link element is a dict with the fields href,
		rel, type, hreflang, title, and length. Href is mandatory for ATOM.

		RSS only supports one link with URL only.
		
		:param link:    Dict or list of dicts with data.
		:param replace: Add or replace old data.

		Example::

			link(...)

		'''
		if link is None and kwargs:
			link = kwargs
		if not link is None:
			if replace or self.__atom_link is None:
				self.__atom_link = []
			self.__atom_link += self.__ensure_format( link, 
					set(['href', 'rel', 'type', 'hreflang', 'title', 'length']),
					set(['href']), 
					{'rel':['alternate', 'enclosure', 'related', 'self', 'via']} )
			# RSS only needs one URL. We use the first link for RSS:
			if len(self.__atom_link) > 0:
				self.__rss_link = self.__atom_link[0]['href']
		# return the set with more information (atom)
		return self.__atom_link


	def category(self, category=None, replace=False, **kwargs):
		if category is None and kwargs:
			category = kwargs
		if not category is None:
			if replace or self.__atom_category is None:
				self.__atom_category = []
			self.__atom_category += self.__ensure_format( 
					category, 
					set(['term', 'schema', 'label']),
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
		'''
		if not domain is None:
			self.__rss_cloud = {'donain':domain, 'port':port, 'path':path,
					'registerProcedure':registerProcedure, 'protocol':protocol}
		return self.__rss_cloud


	def contributor(self, contributor=None, replace=False, **kwargs):
		if contributor is None and kwargs:
			contributor = kwargs
		if not contributor is None:
			if replace or self.__atom_contributor is None:
				self.__atom_contributor = []
			self.__atom_contributor += self.__ensure_format( contributor, 
					set(['name', 'email', 'uri']), set(['name']))
		return self.__atom_contributor


	def generator(self, generator=None, version=None, uri=None):
		if not generator is None:
			self.__atom_generator = {'value':generator}
			if not version in None:
				self.__atom_generator['version'] = version
			if not uri in None:
				self.__atom_generator['uri'] = uri
			self.__rss_generator = generator
		return self.__atom_generator


	def icon(self, icon=None):
		if not icon is None:
			self.__atom_icon = icon
		return self.__atom_icon


	def logo(self, logo=None):
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
		if not rights is None:
			self.__atom_rights = rights
			self.__rss_copyright = rights
		return self.__atom_rights


	def copyright(self, copyright=None):
		return rights( copyright )


	def subtitle(self, subtitle=None):
		if not subtitle is None:
			self.__atom_subtitle   = subtitle
			self.__rss_description = subtitle
		return self.__atom_subtitle


	def description(self, description=None):
		'''Set and get the description of the feed. This is a RSS only element
		which is a phrase or sentence describing the channel. It is roughly the
		same as atom:subtitle. Setting this will also set subtitle.

		:param description: Description/Subtitle of the channel.
		'''
		return self.subtitle( description )


	def docs(self, docs=None):
		if not docs is None:
			self.__rss_docs = docs
		return self.__rss_docs


	def language(self, language=None):
		if not language is None:
			self.__rss_language = language
			self.__atom_feed_xml_lang = language
		return self.__rss_language


	def managingEditor(self, managingEditor=None):
		'''Set or get the value for managingEditor which is the email address for
		person responsible for editorial content.	This is a RSS only value.

		:param managingEditor: Email adress of the managing editor.
		'''
		if not managingEditor is None:
			self.__rss_managingEditor = managingEditor
		return self.__rss_managingEditor


	def pubDate(self, pubDate=None):
		if not pubDate is None:
			if isinstance(pubDate, basestr):
				pubDate = dateutil.parser.parse(pubDate)
			if not isinstance(pubDate, datetime.datetime):
				ValueError('Invalid datetime format')
			if pubDate.tzinfo is None:
				ValueError('Datetime object has no timezone info')
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
		'''
		if not hours is None:
			if not (isinstance(hours, list) or isinstance(hours, set)):
				hours = [hours]
			for h in hours:
				if not h in xrange(24):
					ValueError('Invalid hour %s' % h)
			if replace or not self.__rss_skipHours:
				self.__rss_skipHours = set()
			self.__rss_skipHours |= set(hours)
		return self.__rss_skipHours


	def skipDays(self, days=None, replace=False):
		'''Set or get the value of skipDays, a hint for aggregators telling them
		which days they can skip This is an RSS only value.
		'''
		if not days is None:
			if not (isinstance(days, list) or isinstance(days, set)):
				days = [days]
			for d in days:
				if not d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
						'Friday', 'Saturday', 'Sunday']:
					ValueError('Invalid day %s' % h)
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
		'''
		if not ttl is None:
			self.__rss_ttl = int(ttl)
		return self.__rss_ttl


	def webMaster(self, webMaster=None):
		'''Get and set the value of webMaster, which represents the email address
		for the person responsible for technical issues relating to the feed.
		This is an RSS only value.
		'''
		if not webMaster is None:
			self.__rss_webMaster = webMaster
		return self.__rss_webMaster


	def add_entry(self, feedEntry=None):
		if feedEntry is None:
			feedEntry = FeedEntry()
		self.__feed_entries.append( feedEntry )
		return feedEntry


	def add_item(self, item=None):
		return self.add_entry(item)


class FeedEntry:

	# ATOM
	# required
	__atom_id = None
	__atom_title = None
	__atom_updated = datetime.now(dateutil.tz.tzutc())

	# recommended
	__atom_author = None
	__atom_content = None
	__atom_link = None
	__atom_summary = None

	# optional
	__atom_category = None
	__atom_contributor = None
	__atom_source = None
	__atom_rights = None

	# RSS
	__rss_author = None
	__rss_category = None
	__rss_comments = None
	__rss_description = None
	__rss_enclosure = None
	#@length
	#@type
	#@url
	__rss_guid = None
	#@isPermaLink
	__rss_link = None
	__rss_pubDate = None
	__rss_source = None
	__rss_@url = None
	__rss_title = None


	def __ensure_format(self, val, allowed, required, allowed_values={}):
		if not val:
			return None
		# Make shure that we have a list of dicts. Even if there is only one.
		if not isinstance(val, list):
			val = [val]
		for elem in val:
			if not isinstance(elem, dict):
				raise ValueError('Invalid data (value is no dictionary)')
			if not set(elem.keys()) <= allowed:
				raise ValueError('Data contains invalid keys')
			if not set(elem.keys()) >= required:
				raise ValueError('Data contains not all required keys')
			for k,v in allowed_values.iteritems():
				if elem.get(k) and not elem[k] in v:
					raise ValueError('Invalid value for %s' % k )
		return val


	def atom_entry(self, feed):
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
			if not True in [ l.get('type') == 'alternate' \
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
			if self.__atom_content.get('src'):
				content.attrib['src'] = self.__atom_content['src']
			elif self.__atom_content.get('content'):
				content.text = self.__atom_content.get('content')

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

		if self.__atom_rights:
			rights = etree.SubElement(feed, 'rights')
			rights.text = self.__atom_rights


	
	def title(self, title=None):
		if not title is None:
			self.__atom_title = title
			self.__rss_title = title
		return self.__atom_title


	def id(self, id=None):
		if not id is None:
			self.__atom_id = id
		return self.__atom_id


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
			if isinstance(updated, basestr):
				updated = dateutil.parser.parse(updated)
			if not isinstance(updated, datetime.datetime):
				ValueError('Invalid datetime format')
			if updated.tzinfo is None:
				ValueError('Datetime object has no timezone info')
			self.__atom_updated = updated
			self.__rss_lastBuildDate = updated

		return self.__atom_updated


	def author(self, author=None, replace=False, **kwargs):
		'''Get or set autor data. An author element is a dict containing a name,
		an email adress and a uri. Name is mandatory for ATOM, email is mandatory
		for RSS.
		
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
			self.__atom_author += self.__ensure_format( author, 
					set(['name', 'email', 'uri']), set(['name']))
		return self.__atom_author


	def content(self, content=None, src=None):
		if not src is None:
			self.__atom_content = {'src':src}
		elif not content is None:
			self.__atom_content = {'content':content}
		return self.__atom_content


	def link(self, link=None, replace=False, **kwargs):
		'''Get or set link data. An link element is a dict with the fields href,
		rel, type, hreflang, title, and length. Href is mandatory for ATOM.

		RSS only supports one link with URL only.
		
		:param link:    Dict or list of dicts with data.
		:param replace: Add or replace old data.

		Example::

			link(...)

		'''
		if link is None and kwargs:
			link = kwargs
		if not link is None:
			if replace or self.__atom_link is None:
				self.__atom_link = []
			self.__atom_link += self.__ensure_format( link, 
					set(['href', 'rel', 'type', 'hreflang', 'title', 'length']),
					set(['href']), 
					{'rel':['alternate', 'enclosure', 'related', 'self', 'via']} )
			# RSS only needs one URL. We use the first link for RSS:
			if len(self.__atom_link) > 0:
				self.__rss_link = self.__atom_link[0]['href']
		# return the set with more information (atom)
		return self.__atom_link


	def summary(self, summary=None):
		if not summary is None:
			self.__atom_summary = summary
		return self.__atom_summary


	def category(self, category=None, replace=False, **kwargs):
		if category is None and kwargs:
			category = kwargs
		if not category is None:
			if replace or self.__atom_category is None:
				self.__atom_category = []
			self.__atom_category += self.__ensure_format( 
					category, 
					set(['term', 'schema', 'label']),
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
		if contributor is None and kwargs:
			contributor = kwargs
		if not contributor is None:
			if replace or self.__atom_contributor is None:
				self.__atom_contributor = []
			self.__atom_contributor += self.__ensure_format( contributor, 
					set(['name', 'email', 'uri']), set(['name']))
		return self.__atom_contributor


	def published(self, published=None):
		'''Set or get the published value which ontains the time of the initial
		creation or first availability of the entry.

		The value can either be a string which will automatically be parsed or a
		datetime.datetime object. In any case it is necessary that the value
		include timezone information.

		:param published: The creation date.
		:returns: Creation date as datetime.datetime
		'''
		if not published is None:
			if isinstance(published, basestr):
				published = dateutil.parser.parse(published)
			if not isinstance(published, datetime.datetime):
				ValueError('Invalid datetime format')
			if published.tzinfo is None:
				ValueError('Datetime object has no timezone info')
			self.__atom_published = published
			self.__rss_lastBuildDate = published

		return self.__atom_published


	def rights(self, rights=None):
		if not rights is None:
			self.__atom_rights = rights
		return self.__atom_rights



if __name__ == '__main__':
	fg = FeedGenerator()
	fg.id('http://lernfunk.de/_MEDIAID_123')
	fg.title('Testfeed')
	fg.author( {'name':'Lars Kiesow','email':'lkiesow@uos.de'} )
	fg.link( href='http://example.com', rel='alternate' )
	fg.category(term='test')
	fg.contributor( name='Lars Kiesow', email='lkiesow@uos.de' )
	fg.contributor( name='John Doe', email='jdoe@example.com' )
	fg.icon('http://ex.com/icon.jpg')
	fg.logo('http://ex.com/logo.jpg')
	fg.rights('cc-by')
	fg.subtitle('This is a cool feed!')
	fg.link( href='http://larskiesow.de/test.atom', rel='self' )
	fg.language('de')
	fe = fg.add_entry()
	fe.id('http://lernfunk.de/_MEDIAID_123#1')
	fe.title('First Element')
	fe.content('''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Tamen
			aberramus a proposito, et, ne longius, prorsus, inquam, Piso, si ista
			mala sunt, placet. Aut etiam, ut vestitum, sic sententiam habeas aliam
			domesticam, aliam forensem, ut in fronte ostentatio sit, intus veritas
			occultetur? Cum id fugiunt, re eadem defendunt, quae Peripatetici,
			verba.''')
	fe.summary('Lorem ipsum dolor sit amet, consectetur adipiscing elit...')
	fe.link( href='http://example.com', rel='alternate' )
	fe.author( name='Lars Kiesow', email='lkiesow@uos.de' )


	print fg.atom_str(pretty=True)
	#print fg.rss_str(pretty=True)
