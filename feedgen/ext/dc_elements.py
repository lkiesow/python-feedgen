# -*- coding: utf-8 -*-
'''
	feedgen.ext.podcast
	~~~~~~~~~~~~~~~~~~~

	Extends the FeedGenerator to produce podcasts.

	Descriptions partly taken from
	http://dublincore.org/documents/dcmi-terms/#elements-coverage

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see license.* for more details.
'''

from lxml import etree
from feedgen.ext.base import BaseExtension


class PodcastExtension(BaseExtension):
	'''FeedGenerator extension for podcasts.
	'''


	def __init__(self):
		# http://dublincore.org/documents/usageguide/elements.shtml
		# http://dublincore.org/documents/dces/
		# http://dublincore.org/documents/dcmi-terms/
		self.__dcelem_contributor = None
		self.__dcelem_coverage    = None
		self.__dcelem_creator     = None
		self.__dcelem_date        = None
		self.__dcelem_description = None
		self.__dcelem_format      = None
		self.__dcelem_identifier  = None
		self.__dcelem_language    = None
		self.__dcelem_publisher   = None
		self.__dcelem_relation    = None
		self.__dcelem_rights      = None
		self.__dcelem_source      = None
		self.__dcelem_subject     = None
		self.__dcelem_title       = None
		self.__dcelem_type        = None


	def extend_rss(self, rss_feed):
		'''Create an RSS feed xml structure containing all previously set fields.

		:returns: Tuple containing the feed root element and the element tree.
		'''
		DCELEMENTS_NS = 'http://purl.org/dc/elements/1.1/'
		# Replace the root element to add the new namespace
		nsmap = rss_feed.nsmap
		nsmap['dc'] = DCELEMENTS_NS
		feed = etree.Element('rss', version='2.0', nsmap=nsmap )
		feed[:] = rss_feed[:]
		channel = feed[0]

		#if self.__itunes_author:
		#	author = etree.SubElement(channel, '{%s}author' % ITUNES_NS)
		#	author.text = self.__itunes_author

		# ...

		#if self.__itunes_summary:
		#	summary = etree.SubElement(channel, '{%s}summary' % ITUNES_NS)
		#	summary.text = self.__itunes_summary

		return feed


	def dc_contributor(self, contributor=None, replace=False):
		'''Get or set the dc:contributor which is an entity responsible for
		making contributions to the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-contributor

		If not set, the value of atom:contributor will be used. But setting this
		will on the other hand not set atom:contributor.

		:param contributor: Contributor or list of contributors.
		:param replace: Replace alredy set contributors (deault: False).
		:returns: List of contributors.
		'''
		if not contributor is None:
			if not isinstance(contributor, list):
				contributor = [contributor]
			if replace or not self.__dcelem_contributor:
				self.__dcelem_contributor = []
			self.__dcelem_contributor += contributor
		return self.__dcelem_contributor


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

		References:	[TGN] http://www.getty.edu/research/tools/vocabulary/tgn/index.html

		:param coverage: Coverage of the feed.
		:param replace: Replace already set coverage (default: True).
		:returns: Coverage of the feed.
		'''
		if not coverage is None:
			if not isinstance(coverage, list):
				coverage = [coverage]
			if replace or not self.__dcelem_coverage:
				self.__dcelem_coverage = []
			self.__dcelem_coverage = coverage
		return self.__dcelem_coverage


	def dc_creator(self, creator=None, replace=False):
		'''Get or set the dc:creator which is an entity primarily responsible for
		making the resource. 

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-creator

		If not set, the value of atom:author will be used. But setting this
		will on the other hand not set atom:author.

		:param creator: Creator or list of creators.
		:param replace: Replace alredy set creators (deault: False).
		:returns: List of creators.
		'''
		if not creator is None:
			if not isinstance(creator, list):
				creator = [creator]
			if replace or not self.__dcelem_creator:
				self.__dcelem_creator = []
			self.__dcelem_creator += creator
		return self.__dcelem_creator


	def dc_date(self, date=None, replace=True):
		'''Get or set the dc:date which describes a point or period of time
		associated with an event in the lifecycle of the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-date

		If not set, the value of atom:updated will be used. But setting this
		will on the other hand not set atom:updated.

		:param date: Date or list of dates.
		:param replace: Replace alredy set dates (deault: True).
		:returns: List of dates.
		'''
		if not date is None:
			if not isinstance(date, list):
				date = [date]
			if replace or not self.__dcelem_date:
				self.__dcelem_date = []
			self.__dcelem_date += date
		return self.__dcelem_date


	def dc_description(self, description=None, replace=True):
		'''Get or set the dc:description which is an account of the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-description

		If not set, the value of atom:subtitle will be used. But setting this
		will on the other hand not set atom:subtitle.

		:param description: Description or list of descriptions.
		:param replace: Replace alredy set descriptions (deault: True).
		:returns: List of descriptions.
		'''
		if not description is None:
			if not isinstance(description, list):
				description = [description]
			if replace or not self.__dcelem_description:
				self.__dcelem_description = []
			self.__dcelem_description += description
		return self.__dcelem_description


	def dc_format(self, format=None):
		'''Get or set the dc:format which describes the file format, physical
		medium, or dimensions of the resource.

		For more information see:
		http://dublincore.org/documents/dcmi-terms/#elements-format

		:param format: Format of the resource.
		:returns: Format of the resource.
		'''
		if not format is None:
			self.__dcelem_format = format
		return self.__dcelem_format
