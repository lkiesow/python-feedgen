# -*- coding: utf-8 -*-
'''
    feedgen.ext.media
    ~~~~~~~~~~~~~~~~~

    Extends the feedgen to produce media tags.

    :copyright: 2013-2017, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
'''

from lxml import etree
from feedgen.util import ensure_format
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

        groups = {None: entry}
        for media_content in self.__media_content:
            # Define current media:group
            group = groups.get(media_content.get('group'))
            if group is None:
                group = etree.SubElement(entry, '{%s}group' % MEDIA_NS)
                groups[media_content.get('group')] = group
            # Add content
            content = etree.SubElement(group, '{%s}content' % MEDIA_NS)
            for attr in ('url', 'fileSize', 'type', 'medium', 'isDefault',
                         'expression', 'bitrate', 'framerate', 'samplingrate',
                         'channels', 'duration', 'height', 'width', 'lang'):
                if media_content.get(attr):
                    content.set(attr, media_content[attr])

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

    def content(self, content=None, replace=False, group='default', **kwargs):
        '''Get or set media:content data.

        This method can be called with:
        - the fields of a media:content as keyword arguments
        - the fields of a media:content as a dictionary
        - a list of dictionaries containing the media:content fields

        <media:content> is a sub-element of either <item> or <media:group>.
        Media objects that are not the same content should not be included in
        the same <media:group> element. The sequence of these items implies
        the order of presentation. While many of the attributes appear to be
        audio/video specific, this element can be used to publish any type
        of media. It contains 14 attributes, most of which are optional.

        media:content has the following fields:
        - *url* should specify the direct URL to the media object.
        - *fileSize* number of bytes of the media object.
        - *type* standard MIME type of the object.
        - *medium* type of object (image | audio | video | document |
          executable).
        - *isDefault* determines if this is the default object.
        - *expression* determines if the object is a sample or the full version
          of the object, or even if it is a continuous stream (sample | full |
          nonstop).
        - *bitrate* kilobits per second rate of media.
        - *framerate* number of frames per second for the media object.
        - *samplingrate* number of samples per second taken to create the media
          object. It is expressed in thousands of samples per second (kHz).
        - *channels* number of audio channels in the media object.
        - *duration* number of seconds the media object plays.
        - *height* height of the media object.
        - *width* width of the media object.
        - *lang* is the primary language encapsulated in the media object.

        :param content: Dictionary or list of dictionaries with content data.
        :param replace: Add or replace old data.
        :param group: Media group to put this content in.

        :returns: The media content tag.
        '''
        # Handle kwargs
        if content is None and kwargs:
            content = kwargs
        # Handle new data
        if content is not None:
            # Reset data if we want to replace them
            if replace or self.__media_content is None:
                self.__media_content = []
            # Ensure list
            if not isinstance(content, list):
                content = [content]
            # define media group
            for c in content:
                c['group'] = c.get('group', group)
            self.__media_content += ensure_format(
                    content,
                    set(['url', 'fileSize', 'type', 'medium', 'isDefault',
                         'expression', 'bitrate', 'framerate', 'samplingrate',
                         'channels', 'duration', 'height', 'width', 'lang',
                         'group']),
                    set(['url', 'group']))
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
