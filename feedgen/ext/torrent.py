# -*- coding: utf-8 -*-
'''
	feedgen.ext.torrent
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
		self.__torrent_filename			= None
		self.__torrent_url				= None
		self.__torrent_hash				= None
		self.__torrent_length			= None
		self.__torrent_contentlength	= None

	
	def extend_rss(self, entry):
		'''Add additional fields to an RSS item.

		:param feed: The RSS item XML element to use.
		'''
		enclosure	= etree.SubElement(entry, '{%s}enclosure' % TORRENT_NS)
		guid		= etree.SubElement(entry, '{%s}guid' % TORRENT_NS)
		torrent		= etree.SubElement(entry, '{%s}torrent' % TORRENT_NS)

		enclosure.attrib['type'] = 'application/x-bittorrent'

		if self.__torrent_url:
			enclosure.attrib['url'] = self.__torrent_url
			guid.text = self.__torrent_url
		
		if self.__torrent_filename:
			torrent_filename = etree.SubElement(torrent, '{%s}filename' % TORRENT_NS)
			torrent_filename.text = self.__torrent_filename

		if self.__torrent_length:
			enclosure.attrib['length'] = self.__torrent_length

		if self.__torrent_contentlength:
			torrent_length = etree.SubElement(torrent, '{%s}contentlength' % TORRENT_NS)
			torrent_length.text = self.__torrent_contentlength

		if self.__torrent_hash:
			torrent_hash = etree.SubElement(torrent, '{%s}infohash' % TORRENT_NS)
			torrent_hash.text = self.__torrent_hash
			torrent_magnet = etree.SubElement(torrent, '{%s}magneturi' % TORRENT_NS)
			torrent_magnet.text = 'magnet:?xt=urn:btih:' + self.__torrent_hash


	def torrent_filename(self, torrent_filename=None):
		'''Get or set the name of the torrent file.

		:param torrent_filename: The name of the torrent file.
		:returns: The name of the torrent file.
		'''
		if not torrent_filename is None:
			self.__torrent_filename = torrent_filename
		return self.__torrent_filename

	def torrent_url (self, torrent_url=None):
		'''Get or set the URL of the torrent.

		:param torrent_url: The torrent URL.
		:returns: The torrent URL.
		'''
		if not torrent_url is None:
			self.__torrent_url = torrent_url
		return self.__torrent_url

	def torrent_hash (self, torrent_hash=None):
		'''Get or set the hash of the target file.

		:param torrent_url: The target file hash.
		:returns: The target hash file.
		'''
		if not torrent_hash is None:
			self.__torrent_hash = torrent_hash
		return self.__torrent_hash

	def torrent_length (self, torrent_length=None):
		'''Get or set the size of the torrent file.

		:param torrent_length: The torrent size.
		:returns: The torrent size.
		'''
		if not torrent_length is None:
			self.__torrent_length = torrent_length
		return self.__torrent_length

	def torrent_contentlength (self, torrent_contentlength=None):
		'''Get or set the size of the target file.

		:param torrent_contentlength: The target file size.
		:returns: The target file size.
		'''
		if not torrent_contentlength is None:
			self.__torrent_contentlength = torrent_contentlength
		return self.__torrent_contentlength
