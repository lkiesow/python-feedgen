#!/bin/env python
# -*- coding: utf-8 -*-
'''
	feedgenerator.entry
	~~~~~~~~~~~~~~~~~~~

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see LICENSE for more details.
'''

from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from feedgenerator.util import ensure_format


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
	__rss_guid = None
	__rss_link = None
	__rss_pubDate = None
	__rss_source = None
	__rss_title = None


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


	def rss_entry(self, feed):
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
		for a in self.__rss_author:
			author = etree.SubElement(entry, 'author')
			author.text = a
		if self.__rss_guid:
			guid = etree.SubElement(entry, 'guid')
			guid.text = self.__rss_guid
			guid.attrib['isPermaLink'] = 'false'
		for cat in self.__rss_category or []:
			category = etree.SubElement(channel, 'category')
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
			pubDate = etree.SubElement(channel, 'pubDate')
			pubDate.text = self.__rss_pubDate.strftime(
					'%a, %e %b %Y %H:%M:%S %z')


	
	def title(self, title=None):
		if not title is None:
			self.__atom_title = title
			self.__rss_title = title
		return self.__atom_title


	def id(self, id=None):
		if not id is None:
			self.__atom_id = id
			self.__rss_guid = id
		return self.__atom_id


	def guid(self, guid=None):
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
			self.__atom_author += ensure_format( author, 
					set(['name', 'email', 'uri']), set(['name']))
			self.__rss_author = []
			for a in self.__atom_author:
				if a.get('email'):
					self.__rss_author.append('%s (%s)' % ( a['email'], a['name'] ))
		return self.__atom_author


	def content(self, content=None, src=None):
		if not src is None:
			self.__atom_content = {'src':src}
		elif not content is None:
			self.__atom_content = {'content':content}
			self.__rss_description = content
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
			self.__atom_link += ensure_format( link, 
					set(['href', 'rel', 'type', 'hreflang', 'title', 'length']),
					set(['href']), 
					{'rel':['alternate', 'enclosure', 'related', 'self', 'via']} )
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
		'''
		if not description is None:
			self.__rss_description = description
			if isSummary:
				self.__atom_summary = description
			else:
				self.__atom_content = description
		return self.__rss_description


	def category(self, category=None, replace=False, **kwargs):
		if category is None and kwargs:
			category = kwargs
		if not category is None:
			if replace or self.__atom_category is None:
				self.__atom_category = []
			self.__atom_category += ensure_format( 
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
			self.__atom_contributor += ensure_format( contributor, 
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
			self.__rss_pubDate = published

		return self.__atom_published

	
	def pubdate(self, pubDate=None):
		return self.published(pubDate)


	def rights(self, rights=None):
		if not rights is None:
			self.__atom_rights = rights
		return self.__atom_rights


	def comments(self, comments=None):
		'''Get or set the the value of comments which is the url of the comments
		page for the item. This is a RSS only value.
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
		'''
		if not uri is None:
			self.link( href=url, rel='enclosure', type=type, length=length )
		return self.__rss_enclosure


	def ttl(self, ttl=None):
		'''Get or set the ttl value. It is an RSS only element. ttl stands for
		time to live. It's a number of minutes that indicates how long a channel
		can be cached before refreshing from the source.
		'''
		if not ttl is None:
			self.__rss_ttl = int(ttl)
		return self.__rss_ttl



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

	fg.atom_file('test.atom')
	fg.rss_file('test.rss')

	#print fg.atom_str(pretty=True)
	print fg.rss_str(pretty=True)
