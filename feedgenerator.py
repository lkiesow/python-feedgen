#!/bin/env python
# -*- coding: utf-8 -*-
'''
	feedgenerator
	~~~~~~~~~~~~~

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see LICENSE for more details.
'''

from lxml import etree
from email.Utils import formatdate


class FeedGenerator:

	## ATOM
	# http://www.atomenabled.org/developers/syndication/
	# required
	__atom_id = ''
	__atom_title = ''
	__atom_updated = ''

	# recommended
	__atom_author = '' # {name*, uri, email}
	__atom_link = ''

	'''
	# optional
	category = ''
	contributor = ''
	generator = ''
	icon = ''
	logo = ''
	rights = ''
	subtitle = ''


	## RSS
	title
	link
	description

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

	def __init__(self):
		self.__atom_updated = formatdate()


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
		if self.__atom_author:
			for a in self.__atom_author:
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

		if self.__atom_link:
			for l in self.__atom_link:
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


	def author(self, author=None, replace=False):
		'''Get or set autor data. An author element is a dict containing a name,
		an email adress and a uri. Name is mandatory for ATOM, email is mandatory
		for RSS.
		
		:param author:  Dict or list of dicts with author data.
		:param replace: Add or replace old data.

		Example::

			>>> author( { 'name'='John Doe', 'email'='jdoe@example.com' } )
			[{'name'='John Doe','email'='jdoe@example.com'}]

			>>> author([{'name'='John Doe'},{'name'='Max'}])
			[{'name'='John Doe'},{'name'='Max'}]

		'''
		if not author is None:
			if not isinstance(author, list):
				author = [ author ]
			for a in author:
				if not isinstance(a, dict):
					raise ValueError('Invalid author data (author is no dict)')
				if not set(a.keys()) <= set(['name', 'email', 'uri']):
					raise ValueError('Invalid author data')
			self.__atom_author = author
		return self.__atom_author


	def link(self, link=None, replace=False):
		'''Get or set link data. An link element is a dict with the fields href,
		rel, type, hreflang, title, and length. Href is mandatory for ATOM.
		
		:param link:    Dict or list of dicts with data.
		:param replace: Add or replace old data.

		Example::

			link(...)

		'''
		if not link is None:
			if not isinstance(link, list):
				link = [ link ]
			for l in link:
				if not isinstance(l, dict):
					raise ValueError('Invalid link data (link is no dict)')
				if not set(l.keys()) <= set(['href', 'rel', 'type', 'hreflang', 'title', 'length']):
					raise ValueError('Invalid link data')
				if not set(l.keys()) >= set(['href']):
					raise ValueError('Invalid link data (no href)')
				if l.get('rel') and l['rel'] not in \
						['alternate', 'enclosure', 'related', 'self', 'via']:
					raise ValueError('Invalid rel type')
			self.__atom_link = link
		return self.__atom_link


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
	fg.id('123')
	fg.title('Testfeed')
	fg.author( {'name':'Lars Kiesow','email':'lkiesow@uos.de'} )
	fg.link( {'href':'http://example.com', 'rel':'alternate'} )
	print fg.atom_str()
