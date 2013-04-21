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


class FeedGenerator:

	## ATOM
	# http://www.atomenabled.org/developers/syndication/
	# required
	__atom_id = None
	__atom_title = None
	__atom_updated = datetime.utcnow().isoformat('T')+'Z'

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

	## RSS
	__rss_title = None
	__rss_link = None
	__rss_description = None

	'''
	category
	cloud
	copyright
	docs
	generator
	image
	language
	lastBuildDate
	managingEditor
	pubDate
	rating
	skipHours
	skipDays
	textInput
	ttl
	webMaster


	# feed
	# rss -> channel
	'''


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


	def atom_str(self):
		feed    = etree.Element('feed',  xmlns='http://www.w3.org/2005/Atom')
		doc     = etree.ElementTree(feed)
		if not ( self.__atom_id and self.__atom_title and self.__atom_updated ):
			raise ValueError('Required fields not set')
		id      = etree.SubElement(feed, 'id')
		id.text = self.__atom_id
		title   = etree.SubElement(feed, 'title')
		title.text = self.__atom_title
		updated   = etree.SubElement(feed, 'updated')
		updated.text = self.__atom_updated

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

		return etree.tostring(feed, pretty_print=True)
		'''
		outFile = open('homemade.xml', 'w')
		doc.write(outFile)
		'''

	
	def title(self, title=None):
		if not title is None:
			self.__atom_title = title
		return self.__atom_title


	def id(self, id=None):
		if not id is None:
			self.__atom_id = id
		return self.__atom_id


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


	def generator(self, generator=None, version=None, uri=None):
		if not generator is None:
			self.__atom_generator = {'value':generator}
			if not version in None:
				self.__atom_generator['version'] = version
			if not uri in None:
				self.__atom_generator['uri'] = uri
		return self.__atom_generator


	def icon(self, icon=None):
		if not icon is None:
			self.__atom_icon = icon
		return self.__atom_icon


	def logo(self, logo=None):
		if not logo is None:
			self.__atom_logo = logo
		return self.__atom_logo


	def rights(self, rights=None):
		if not rights is None:
			self.__atom_rights = rights
		return self.__atom_rights


	def subtitle(self, subtitle=None):
		if not subtitle is None:
			self.__atom_subtitle = subtitle
		return self.__atom_subtitle


class FeedEntry:

	'''
	# ATOM
	# required
	id
	title
	updated

	# recommended
	author
	content
	link
	summary

	# optional
	category
	contributor
	source
	rights

	# RSS
	author
	category
	#@domain
	comments
	description
	enclosure
	#@length
	#@type
	#@url
	guid
	#@isPermaLink
	link
	pubDate
	source
	@url
	title
	'''

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
	print fg.atom_str()
