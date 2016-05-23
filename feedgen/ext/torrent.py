# -*- coding: utf-8 -*-
'''
	feedgen.ext.podcast
	~~~~~~~~~~~~~~~~~~~

	Extends the FeedGenerator to produce torrent feeds.

	:copyright: 2016, Raspbeguy <raspbeguy@hashtagueule.fr>

	:license: FreeBSD and LGPL, see license.* for more details.
'''

from lxml import etree
from feedgen.ext.base import BaseExtension,BaseEntryExtension

TORRENT_NS = 'http://xmlns.ezrss.it/0.1/dtd/'

class TorrentExtension(BaseExtension):
	'''FeedGenerator extension for torrent feeds.
	'''


	def extend_ns(self):
		return {'torrent' : TORRENT_NS}


class TorrentEntryExtension(BaseEntryExtension):
	'''FeedEntry extention for torrent feeds
	'''


	def __init__(self):
		self.__torrent_enclosure	= None
		self.__torrent_media		= None
		self.__torrent_guid			= None

	
	def extend_rss(self, entry):
		'''Add additional fields to an RSS item.

		:param feed: The RSS item XML element to use.
		'''
		if self.__torrent_enclosure:
			enclosure = etree.SubElement(entry, '{%s}enclosure' % TORRENT_NS)
