# -*- coding: utf-8 -*-
'''
	feedgen.ext.dc
	~~~~~~~~~~~~~~~~~~~

	Extends the FeedGenerator to add Dubline Core Elements to the feeds.

	Descriptions partly taken from
	http://dublincore.org/documents/dcmi-terms/#elements-coverage

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see license.* for more details.
'''

from lxml import etree
from feedgen.ext.base import BaseExtension, BaseEntryExtension


class DcBaseExtension(BaseExtension):
	'''Dublin Core Elements extension for podcasts.
	'''


	def __init__(self):
		# http://dublincore.org/documents/usageguide/elements.shtml
		# http://dublincore.org/documents/dces/
		# http://dublincore.org/documents/dcmi-terms/
		self._dcelem_contributor = None
		self._dcelem_coverage    = None
		self._dcelem_creator     = None
		self._dcelem_date        = None
		self._dcelem_description = None
		self._dcelem_format      = None
		self._dcelem_identifier  = None
		self._dcelem_language    = None
		self._dcelem_publisher   = None
		self._dcelem_relation    = None
		self._dcelem_rights      = None
		self._dcelem_source      = None
		self._dcelem_subject     = None
		self._dcelem_title       = None
		self._dcelem_type        = None

	def extend_ns(self):
		return {'dc' : 'http://purl.org/dc/elements/1.1/'}

	def extend_atom(self, atom_feed):
		'''Create an Atom feed xml structure containing all previously set fields.

		:returns: The feed root element
		'''
		DCELEMENTS_NS = 'http://purl.org/dc/elements/1.1/'
		
		feed = atom_feed

		for elem in ['contributor', 'coverage', 'creator', 'date', 'description',
				'language', 'publisher', 'relation', 'rights', 'source', 'subject',
				'title', 'type']:
			if hasattr(self, '_dcelem_%s' % elem):
				for val in getattr(self, '_dcelem_%s' % elem) or []:
					node = etree.SubElement(feed, '{%s}%s' % (DCELEMENTS_NS,elem))
					node.text = val

		if self._dcelem_format:
			node = etree.SubElement(feed, '{%s}format' % DCELEMENTS_NS)
			node.text = format

		if self._dcelem_identifier:
			node = etree.SubElement(feed, '{%s}identifier' % DCELEMENTS_NS)
			node.text = identifier

		return feed


	def extend_rss(self, rss_feed):
		'''Create an RSS feed xml structure containing all previously set fields.

		:returns: Tuple containing the feed root element and the element tree.
		'''
		DCELEMENTS_NS = 'http://purl.org/dc/elements/1.1/'
		channel = rss_feed[0]

		for elem in ['contributor', 'coverage', 'creator', 'date', 'description',
				'language', 'publisher', 'relation', 'rights', 'source', 'subject',
				'title', 'type']:
			if hasattr(self, '_dcelem_%s' % elem):
				for val in getattr(self, '_dcelem_%s' % elem) or []:
					node = etree.SubElement(channel, '{%s}%s' % (DCELEMENTS_NS,elem))
					node.text = val

		if self._dcelem_format:
			node = etree.SubElement(channel, '{%s}format' % DCELEMENTS_NS)
			node.text = format

		if self._dcelem_identifier:
			node = etree.SubElement(channel, '{%s}identifier' % DCELEMENTS_NS)
			node.text = identifier

		return rss_feed


	def dc_contributor(self, contributor=None, replace=False):
		'''Get or set the dc:contributor which is an entity responsible for
		making contributions to the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-contributor

		:param contributor: Contributor or list of contributors.
		:param replace: Replace alredy set contributors (deault: False).
		:returns: List of contributors.
		'''
		if not contributor is None:
			if not isinstance(contributor, list):
				contributor = [contributor]
			if replace or not self._dcelem_contributor:
				self._dcelem_contributor = []
			self._dcelem_contributor += contributor
		return self._dcelem_contributor


	def dc_coverage(self, coverage=None, replace=True):
		'''Get or set the dc:coverage which indicated the spatial or temporal
		topic of the resource, the spatial applicability of the resource, or the
		jurisdiction under which the resource is relevant.

		Spatial topic and spatial applicability may be a named place or a
		location specified by its geographic coordinates. Temporal topic may be a
		named period, date, or date range. A jurisdiction may be a named
		administrative entity or a geographic place to which the resource
		applies. Recommended best practice is to use a controlled vocabulary such
		as the Thesaurus of Geographic Names [TGN]. Where appropriate, named
		places or time periods can be used in preference to numeric identifiers
		such as sets of coordinates or date ranges.

		References: [TGN] http://www.getty.edu/research/tools/vocabulary/tgn/index.html

		:param coverage: Coverage of the feed.
		:param replace: Replace already set coverage (default: True).
		:returns: Coverage of the feed.
		'''
		if not coverage is None:
			if not isinstance(coverage, list):
				coverage = [coverage]
			if replace or not self._dcelem_coverage:
				self._dcelem_coverage = []
			self._dcelem_coverage = coverage
		return self._dcelem_coverage


	def dc_creator(self, creator=None, replace=False):
		'''Get or set the dc:creator which is an entity primarily responsible for
		making the resource. 

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-creator

		:param creator: Creator or list of creators.
		:param replace: Replace alredy set creators (deault: False).
		:returns: List of creators.
		'''
		if not creator is None:
			if not isinstance(creator, list):
				creator = [creator]
			if replace or not self._dcelem_creator:
				self._dcelem_creator = []
			self._dcelem_creator += creator
		return self._dcelem_creator


	def dc_date(self, date=None, replace=True):
		'''Get or set the dc:date which describes a point or period of time
		associated with an event in the lifecycle of the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-date

		:param date: Date or list of dates.
		:param replace: Replace alredy set dates (deault: True).
		:returns: List of dates.
		'''
		if not date is None:
			if not isinstance(date, list):
				date = [date]
			if replace or not self._dcelem_date:
				self._dcelem_date = []
			self._dcelem_date += date
		return self._dcelem_date


	def dc_description(self, description=None, replace=True):
		'''Get or set the dc:description which is an account of the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-description

		:param description: Description or list of descriptions.
		:param replace: Replace alredy set descriptions (deault: True).
		:returns: List of descriptions.
		'''
		if not description is None:
			if not isinstance(description, list):
				description = [description]
			if replace or not self._dcelem_description:
				self._dcelem_description = []
			self._dcelem_description += description
		return self._dcelem_description


	def dc_format(self, format=None, replace=True):
		'''Get or set the dc:format which describes the file format, physical
		medium, or dimensions of the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-format

		:param format: Format of the resource or list of formats.
		:param replace: Replace alredy set format (deault: True).
		:returns: Format of the resource.
		'''
		if not format is None:
			if not isinstance(format, list):
				format = [format]
			if replace or not self._dcelem_format:
				self._dcelem_format = []
			self._dcelem_format += format
		return self._dcelem_format


	def dc_identifier(self, identifier=None, replace=True):
		'''Get or set the dc:identifier which should be an unambiguous reference
		to the resource within a given context.

		If not set, the value of atom:id will be used. But setting this value
		will on the other hand not set atom:id.

		For more inidentifierion see:
		http://dublincore.org/documents/dcmi-terms/#elements-identifier

		:param identifier: Identifier of the resource or list of identifiers.
		:param replace: Replace alredy set format (deault: True).
		:returns: Identifiers of the resource.
		'''
		if not identifier is None:
			if not isinstance(identifier, list):
				identifier = [identifier]
			if replace or not self._dcelem_identifier:
				self._dcelem_identifier = []
			self._dcelem_identifier += identifier


	def dc_language(self, language=None, replace=True):
		'''Get or set the dc:language which describes a language of the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-language

		:param language: Language or list of languages.
		:param replace: Replace alredy set languages (deault: True).
		:returns: List of languages.
		'''
		if not language is None:
			if not isinstance(language, list):
				language = [language]
			if replace or not self._dcelem_language:
				self._dcelem_language = []
			self._dcelem_language += language
		return self._dcelem_language


	def dc_publisher(self, publisher=None, replace=False):
		'''Get or set the dc:publisher which is an entity responsible for making
		the resource available.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-publisher

		:param publisher: Publisher or list of publishers.
		:param replace: Replace alredy set publishers (deault: False).
		:returns: List of publishers.
		'''
		if not publisher is None:
			if not isinstance(publisher, list):
				publisher = [publisher]
			if replace or not self._dcelem_publisher:
				self._dcelem_publisher = []
			self._dcelem_publisher += publisher
		return self._dcelem_publisher


	def dc_relation(self, relation=None, replace=False):
		'''Get or set the dc:relation which describes a related ressource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-relation

		:param relation: Relation or list of relations.
		:param replace: Replace alredy set relations (deault: False).
		:returns: List of relations.
		'''
		if not relation is None:
			if not isinstance(relation, list):
				relation = [relation]
			if replace or not self._dcelem_relation:
				self._dcelem_relation = []
			self._dcelem_relation += relation
		return self._dcelem_relation


	def dc_rights(self, rights=None, replace=False):
		'''Get or set the dc:rights which may contain information about rights
		held in and over the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-rights

		:param rights: Rights information or list of rights information.
		:param replace: Replace alredy set rightss (deault: False).
		:returns: List of rights information.
		'''
		if not rights is None:
			if not isinstance(rights, list):
				rights = [rights]
			if replace or not self._dcelem_rights:
				self._dcelem_rights = []
			self._dcelem_rights += rights
		return self._dcelem_rights


	def dc_source(self, source=None, replace=False):
		'''Get or set the dc:source which is a related resource from which the
		described resource is derived.

		The described resource may be derived from the related resource in whole
		or in part. Recommended best practice is to identify the related resource
		by means of a string conforming to a formal identification system.


		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-source

		:param source: Source or list of sources.
		:param replace: Replace alredy set sources (deault: False).
		:returns: List of sources.
		'''
		if not source is None:
			if not isinstance(source, list):
				source = [source]
			if replace or not self._dcelem_source:
				self._dcelem_source = []
			self._dcelem_source += source
		return self._dcelem_source


	def dc_subject(self, subject=None, replace=False):
		'''Get or set the dc:subject which describes the topic of the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-subject

		:param subject: Subject or list of subjects.
		:param replace: Replace alredy set subjects (deault: False).
		:returns: List of subjects.
		'''
		if not subject is None:
			if not isinstance(subject, list):
				subject = [subject]
			if replace or not self._dcelem_subject:
				self._dcelem_subject = []
			self._dcelem_subject += subject
		return self._dcelem_subject


	def dc_title(self, title=None, replace=True):
		'''Get or set the dc:title which is a name given to the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-title

		:param title: Title or list of titles.
		:param replace: Replace alredy set titles (deault: False).
		:returns: List of titles.
		'''
		if not title is None:
			if not isinstance(title, list):
				title = [title]
			if replace or not self._dcelem_title:
				self._dcelem_title = []
			self._dcelem_title += title
		return self._dcelem_title


	def dc_type(self, type=None, replace=False):
		'''Get or set the dc:type which describes the nature or genre of the
		resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-type

		:param type: Type or list of types.
		:param replace: Replace alredy set types (deault: False).
		:returns: List of types.
		'''
		if not type is None:
			if not isinstance(type, list):
				type = [type]
			if replace or not self._dcelem_type:
				self._dcelem_type = []
			self._dcelem_type += type
		return self._dcelem_type

class DcExtension(DcBaseExtension):
	'''Dublin Core Elements extension for podcasts.
	'''

class DcEntryExtension(DcBaseExtension):
	'''Dublin Core Elements extension for podcasts.
	'''
	def extend_atom(self, entry):
		'''NYI. Differs from RSS Implementation?
		
		'''
		return entry

	def extend_rss(self, item):
		'''Add dc elements to a RSS item. Alters the item itself.

		:returns: The item element.
		'''
		DCELEMENTS_NS = 'http://purl.org/dc/elements/1.1/'

		for elem in ['contributor', 'coverage', 'creator', 'date', 'description',
				'language', 'publisher', 'relation', 'rights', 'source', 'subject',
				'title', 'type']:
			if hasattr(self, '_dcelem_%s' % elem):
				for val in getattr(self, '_dcelem_%s' % elem) or []:
					node = etree.SubElement(item, '{%s}%s' % (DCELEMENTS_NS,elem))
					node.text = val

		if self._dcelem_format:
			node = etree.SubElement(item, '{%s}format' % DCELEMENTS_NS)
			node.text = format

		if self._dcelem_identifier:
			node = etree.SubElement(item, '{%s}identifier' % DCELEMENTS_NS)
			node.text = identifier

		return item
