# -*- coding: utf-8 -*-
'''
    feedgen.ext.base
    ~~~~~~~~~~~~~~~~

    Basic FeedGenerator extension which does nothing but provides all necessary
    methods.

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
'''


class BaseExtension(object):
    '''Basic FeedGenerator extension.
    '''
    def extend_ns(self):
        '''Returns a dict that will be used in the namespace map for the feed.
        '''
        return dict()

    def extend_rss(self, feed):
        '''Extend a RSS feed xml structure containing all previously set fields.

        :param feed: The feed xml root element.
        :returns: The feed root element.
        '''
        return feed

    def extend_atom(self, feed):
        '''Extend an ATOM feed xml structure containing all previously set
        fields.

        :param feed: The feed xml root element.
        :returns: The feed root element.
        '''
        return feed


class BaseEntryExtension(BaseExtension):
    '''Basic FeedEntry extension.
    '''
