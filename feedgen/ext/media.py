# -*- coding: utf-8 -*-
'''
    feedgen.ext.media
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Extends the feedgen to produce media tags.

    :copyright: 2013-2017, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
'''

from lxml import etree
from feedgen.ext.base import BaseExtension, BaseEntryExtension

MEDIA_NS = 'http://search.yahoo.com/mrss/'


class MediaExtension(BaseExtension):
    '''FeedGenerator extension for torrent feeds.
    '''

    def extend_ns(self):
        return {'media': MEDIA_NS}


class MediaEntryExtension(BaseEntryExtension):
    '''FeedEntry extension for media tags.
    '''

    def __init__(self):
        self.__media_content = []
        self.__media_thumbnail = None

    def extend_atom(self, entry):
        '''Add additional fields to an RSS item.

        :param feed: The RSS item XML element to use.
        '''

        group = etree.SubElement(entry, '{%s}group' % MEDIA_NS)
        if self.__media_content:
            content = etree.SubElement(group, '{%s}content' % MEDIA_NS)
            if self.__media_content.get('url'):
                content.set('url', self.__media_content.get('url'))
            if self.__media_content.get('fileSize'):
                content.set('fileSize', self.__media_content.get('fileSize'))
            if self.__media_content.get('type'):
                content.set('type', self.__media_content.get('type'))
            if self.__media_content.get('medium'):
                content.set('medium', self.__media_content.get('medium'))
            if self.__media_content.get('isDefault'):
                content.set('isDefault', self.__media_content.get('isDefault'))
            if self.__media_content.get('expression'):
                content.set(
                    'expression', self.__media_content.get('expression'))
            if self.__media_content.get('bitrate'):
                content.set('bitrate', self.__media_content.get('bitrate'))
            if self.__media_content.get('framerate'):
                content.set('framerate', self.__media_content.get('framerate'))
            if self.__media_content.get('samplingrate'):
                content.set('samplingrate',
                            self.__media_content.get('samplingrate'))
            if self.__media_content.get('channels'):
                content.set('channels', self.__media_content.get('channels'))
            if self.__media_content.get('duration'):
                content.set('duration', self.__media_content.get('duration'))
            if self.__media_content.get('height'):
                content.set('height', self.__media_content.get('height'))
            if self.__media_content.get('width'):
                content.set('width', self.__media_content.get('width'))
            if self.__media_content.get('lang'):
                content.set('lang', self.__media_content.get('lang'))
        if self.__media_thumbnail:
            thumbnail = etree.SubElement(group, '{%s}thumbnail' % MEDIA_NS)
            if self.__media_thumbnail.get('url'):
                thumbnail.set('url', self.__media_thumbnail.get('url'))
            if self.__media_thumbnail.get('height'):
                thumbnail.set('height', self.__media_thumbnail.get('height'))
            if self.__media_thumbnail.get('width'):
                thumbnail.set('width', self.__media_thumbnail.get('width'))
            if self.__media_thumbnail.get('lang'):
                thumbnail.set('lang', self.__media_thumbnail.get('lang'))

        return entry

    def extend_rss(self, item):
        return self.extend_atom(item)

    def content(self, url=None, fileSize=None, type=None, medium=None,
                isDefault=None, expression=None, bitrate=None, framerate=None,
                samplingrate=None, channels=None, duration=None, height=None,
                width=None, lang=None):
        '''<media:content> is a sub-element of either <item> or <media:group>.
        Media objects that are not the same content should not be included in
        the same <media:group> element. The sequence of these items implies
        the order of presentation. While many of the attributes appear to be
        audio/video specific, this element can be used to publish any type
        of media. It contains 14 attributes, most of which are optional.

        :param url: should specify the direct URL to the media object.
        :param fileSize: number of bytes of the media object.
        :param type: standard MIME type of the object.
        :param medium: type of object
                       (image | audio | video | document | executable).
        :param isDefault: determines if this is the default object.
        :param expression: determines if the object is a sample or the full
                           version of the object, or even if it is a
                           continuous stream (sample | full | nonstop).
        :param bitrate: kilobits per second rate of media.
        :param framerate: number of frames per second for the media object.
        :param samplingrate: number of samples per second taken to create the
                             media object. It is expressed in thousands of
                             samples per second (kHz).
        :param channels: number of audio channels in the media object.
        :param duration: number of seconds the media object plays.
        :param height: height of the media object.
        :param width: width of the media object.
        :param lang: is the primary language encapsulated in the media object.

        :returns: The media content tag.
        '''

        if url is not None:
            self.__media_content = {'url': url}
            if fileSize is not None:
                self.__media_content['fileSize'] = fileSize
            if type is not None:
                self.__media_content['type'] = type
            if medium is not None:
                self.__media_content['medium'] = medium
            if isDefault is not None:
                self.__media_content['isDefault'] = isDefault
            if expression is not None:
                self.__media_content['expression'] = expression
            if bitrate is not None:
                self.__media_content['bitrate'] = bitrate
            if framerate is not None:
                self.__media_content['framerate'] = framerate
            if samplingrate is not None:
                self.__media_content['samplingrate'] = samplingrate
            if channels is not None:
                self.__media_content['channels'] = channels
            if duration is not None:
                self.__media_content['duration'] = duration
            if height is not None:
                self.__media_content['height'] = height
            if width is not None:
                self.__media_content['width'] = width
            if lang is not None:
                self.__media_content['lang'] = lang

        return self.__media_content

    def thumbnail(self, url=None, height=None, width=None, time=None):
        '''Allows particular images to be used as representative images for
        the media object. If multiple thumbnails are included, and time
        coding is not at play, it is assumed that the images are in order
        of importance. It has one required attribute and three optional
        attributes.

        :param url: should specify the direct URL to the media object.
        :param height: height of the media object.
        :param width: width of the media object.
        :param time: specifies the time offset in relation to the media object.

        :returns: The media thumbnail tag.
        '''

        if url is not None:
            self.__media_thumbnail = {'url': url}
            if height is not None:
                self.__media_thumbnail['height'] = height
            if width is not None:
                self.__media_thumbnail['width'] = width
            if time is not None:
                self.__media_thumbnail['time'] = time

        return self.__media_thumbnail
