# -*- coding: utf-8 -*-
'''
    feedgen.ext.torrent
    ~~~~~~~~~~~~~~~~~~~

    Extends the FeedGenerator to produce torrent feeds.

    :copyright: 2016, Raspbeguy <raspbeguy@hashtagueule.fr>

    :license: FreeBSD and LGPL, see license.* for more details.
'''

from feedgen.ext.base import BaseEntryExtension, BaseExtension
from feedgen.util import xml_elem

TORRENT_NS = 'http://xmlns.ezrss.it/0.1/dtd/'


class TorrentExtension(BaseExtension):
    '''FeedGenerator extension for torrent feeds.
    '''
    def extend_ns(self):
        return {'torrent': TORRENT_NS}


class TorrentEntryExtension(BaseEntryExtension):
    '''FeedEntry extension for torrent feeds
    '''
    def __init__(self):
        self.__torrent_filename = None
        self.__torrent_infohash = None
        self.__torrent_contentlength = None
        self.__torrent_seeds = None
        self.__torrent_peers = None
        self.__torrent_verified = None

    def extend_rss(self, entry):
        '''Add additional fields to an RSS item.

        :param feed: The RSS item XML element to use.
        '''
        if self.__torrent_filename:
            filename = xml_elem('{%s}filename' % TORRENT_NS, entry)
            filename.text = self.__torrent_filename

        if self.__torrent_contentlength:
            contentlength = xml_elem('{%s}contentlength' % TORRENT_NS, entry)
            contentlength.text = self.__torrent_contentlength

        if self.__torrent_infohash:
            infohash = xml_elem('{%s}infohash' % TORRENT_NS, entry)
            infohash.text = self.__torrent_infohash
            magnet = xml_elem('{%s}magneturi' % TORRENT_NS, entry)
            magnet.text = 'magnet:?xt=urn:btih:' + self.__torrent_infohash

        if self.__torrent_seeds:
            seeds = xml_elem('{%s}seed' % TORRENT_NS, entry)
            seeds.text = self.__torrent_seeds

        if self.__torrent_peers:
            peers = xml_elem('{%s}peers' % TORRENT_NS, entry)
            peers.text = self.__torrent_peers

        if self.__torrent_verified:
            verified = xml_elem('{%s}verified' % TORRENT_NS, entry)
            verified.text = self.__torrent_verified

    def filename(self, torrent_filename=None):
        '''Get or set the name of the torrent file.

        :param torrent_filename: The name of the torrent file.
        :returns: The name of the torrent file.
        '''
        if torrent_filename is not None:
            self.__torrent_filename = torrent_filename
        return self.__torrent_filename

    def infohash(self, torrent_infohash=None):
        '''Get or set the hash of the target file.

        :param torrent_infohash: The target file hash.
        :returns: The target hash file.
        '''
        if torrent_infohash is not None:
            self.__torrent_infohash = torrent_infohash
        return self.__torrent_infohash

    def contentlength(self, torrent_contentlength=None):
        '''Get or set the size of the target file.

        :param torrent_contentlength: The target file size.
        :returns: The target file size.
        '''
        if torrent_contentlength is not None:
            self.__torrent_contentlength = torrent_contentlength
        return self.__torrent_contentlength

    def seeds(self, torrent_seeds=None):
        '''Get or set the number of seeds.

        :param torrent_seeds: The seeds number.
        :returns: The seeds number.
        '''
        if torrent_seeds is not None:
            self.__torrent_seeds = torrent_seeds
        return self.__torrent_seeds

    def peers(self, torrent_peers=None):
        '''Get or set the number od peers

        :param torrent_infohash: The peers number.
        :returns: The peers number.
        '''
        if torrent_peers is not None:
            self.__torrent_peers = torrent_peers
        return self.__torrent_peers

    def verified(self, torrent_verified=None):
        '''Get or set the number of verified peers.

        :param torrent_infohash: The verified peers number.
        :returns: The verified peers number.
        '''
        if torrent_verified is not None:
            self.__torrent_verified = torrent_verified
        return self.__torrent_verified
