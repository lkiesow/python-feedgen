# -*- coding: utf-8 -*-
#
# Copyright 2015 Kenichi Sato <ksato9700@gmail.com>
#

'''
Extends FeedGenerator to support Syndication module

See below for details
http://web.resource.org/rss/1.0/modules/syndication/
'''

from feedgen.ext.base import BaseExtension
from feedgen.util import xml_elem

SYNDICATION_NS = 'http://purl.org/rss/1.0/modules/syndication/'
PERIOD_TYPE = ('hourly', 'daily', 'weekly', 'monthly', 'yearly')


def _set_value(channel, name, value):
    if value:
        newelem = xml_elem('{%s}' % SYNDICATION_NS + name, channel)
        newelem.text = value


class SyndicationExtension(BaseExtension):
    def __init__(self):
        self._update_period = None
        self._update_freq = None
        self._update_base = None

    def extend_ns(self):
        return {'sy': SYNDICATION_NS}

    def extend_rss(self, rss_feed):
        channel = rss_feed[0]
        _set_value(channel, 'UpdatePeriod', self._update_period)
        _set_value(channel, 'UpdateFrequency', str(self._update_freq))
        _set_value(channel, 'UpdateBase', self._update_base)

    def update_period(self, value):
        if value not in PERIOD_TYPE:
            raise ValueError('Invalid update period value')
        self._update_period = value
        return self._update_period

    def update_frequency(self, value):
        if type(value) is not int or value <= 0:
            raise ValueError('Invalid update frequency value')
        self._update_freq = value
        return self._update_freq

    def update_base(self, value):
        # the value should be in W3CDTF format
        self._update_base = value
        return self._update_base


class SyndicationEntryExtension(BaseExtension):
    pass
