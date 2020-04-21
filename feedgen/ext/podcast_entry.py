# -*- coding: utf-8 -*-
'''
    feedgen.ext.podcast_entry
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Extends the feedgen to produce podcasts.

    :copyright: 2013-2016, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
'''

from feedgen.ext.base import BaseEntryExtension
from feedgen.util import xml_elem


class PodcastEntryExtension(BaseEntryExtension):
    '''FeedEntry extension for podcasts.
    '''

    def __init__(self):
        # ITunes tags
        # http://www.apple.com/itunes/podcasts/specs.html#rss
        self.__itunes_author = None
        self.__itunes_block = None
        self.__itunes_image = None
        self.__itunes_duration = None
        self.__itunes_explicit = None
        self.__itunes_is_closed_captioned = None
        self.__itunes_order = None
        self.__itunes_subtitle = None
        self.__itunes_summary = None
        self.__itunes_season = None
        self.__itunes_episode = None
        self.__itunes_title = None
        self.__itunes_episode_type = None

    def extend_rss(self, entry):
        '''Add additional fields to an RSS item.

        :param feed: The RSS item XML element to use.
        '''
        ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'

        if self.__itunes_author:
            author = xml_elem('{%s}author' % ITUNES_NS, entry)
            author.text = self.__itunes_author

        if self.__itunes_block is not None:
            block = xml_elem('{%s}block' % ITUNES_NS, entry)
            block.text = 'yes' if self.__itunes_block else 'no'

        if self.__itunes_image:
            image = xml_elem('{%s}image' % ITUNES_NS, entry)
            image.attrib['href'] = self.__itunes_image

        if self.__itunes_duration:
            duration = xml_elem('{%s}duration' % ITUNES_NS, entry)
            duration.text = self.__itunes_duration

        if self.__itunes_explicit in ('yes', 'no', 'clean'):
            explicit = xml_elem('{%s}explicit' % ITUNES_NS, entry)
            explicit.text = self.__itunes_explicit

        if self.__itunes_is_closed_captioned is not None:
            is_closed_captioned = xml_elem(
                    '{%s}isClosedCaptioned' % ITUNES_NS, entry)
            if self.__itunes_is_closed_captioned:
                is_closed_captioned.text = 'yes'
            else:
                is_closed_captioned.text = 'no'

        if self.__itunes_order is not None and self.__itunes_order >= 0:
            order = xml_elem('{%s}order' % ITUNES_NS, entry)
            order.text = str(self.__itunes_order)

        if self.__itunes_subtitle:
            subtitle = xml_elem('{%s}subtitle' % ITUNES_NS, entry)
            subtitle.text = self.__itunes_subtitle

        if self.__itunes_summary:
            summary = xml_elem('{%s}summary' % ITUNES_NS, entry)
            summary.text = self.__itunes_summary

        if self.__itunes_season:
            season = xml_elem('{%s}season' % ITUNES_NS, entry)
            season.text = str(self.__itunes_season)

        if self.__itunes_episode:
            episode = xml_elem('{%s}episode' % ITUNES_NS, entry)
            episode.text = str(self.__itunes_episode)

        if self.__itunes_title:
            title = xml_elem('{%s}title' % ITUNES_NS, entry)
            title.text = self.__itunes_title

        if self.__itunes_episode_type in ('full', 'trailer', 'bonus'):
            episode_type = xml_elem('{%s}episodeType' % ITUNES_NS, entry)
            episode_type.text = self.__itunes_episode_type
        return entry

    def itunes_author(self, itunes_author=None):
        '''Get or set the itunes:author of the podcast episode. The content of
        this tag is shown in the Artist column in iTunes. If the tag is not
        present, iTunes uses the contents of the <author> tag. If
        <itunes:author> is not present at the feed level, iTunes will use the
        contents of <managingEditor>.

        :param itunes_author: The author of the podcast.
        :returns: The author of the podcast.
        '''
        if itunes_author is not None:
            self.__itunes_author = itunes_author
        return self.__itunes_author

    def itunes_block(self, itunes_block=None):
        '''Get or set the ITunes block attribute. Use this to prevent episodes
        from appearing in the iTunes podcast directory.

        :param itunes_block: Block podcast episodes.
        :returns: If the podcast episode is blocked.
        '''
        if itunes_block is not None:
            self.__itunes_block = itunes_block
        return self.__itunes_block

    def itunes_image(self, itunes_image=None):
        '''Get or set the image for the podcast episode. This tag specifies the
        artwork for your podcast. Put the URL to the image in the href
        attribute.  iTunes prefers square .jpg images that are at least
        1400x1400 pixels, which is different from what is specified for the
        standard RSS image tag.  In order for a podcast to be eligible for an
        iTunes Store feature, the accompanying image must be at least 1400x1400
        pixels.

        iTunes supports images in JPEG and PNG formats with an RGB color space
        (CMYK is not supported). The URL must end in ".jpg" or ".png". If the
        <itunes:image> tag is not present, iTunes will use the contents of the
        RSS image tag.

        If you change your podcast’s image, also change the file’s name. iTunes
        may not change the image if it checks your feed and the image URL is
        the same. The server hosting your cover art image must allow HTTP head
        requests for iTS to be able to automatically update your cover art.

        :param itunes_image: Image of the podcast.
        :returns: Image of the podcast.
        '''
        if itunes_image is not None:
            if itunes_image.endswith('.jpg') or itunes_image.endswith('.png'):
                self.__itunes_image = itunes_image
            else:
                raise ValueError('Image file must be png or jpg')
        return self.__itunes_image

    def itunes_duration(self, itunes_duration=None):
        '''Get or set the duration of the podcast episode. The content of this
        tag is shown in the Time column in iTunes.

        The tag can be formatted HH:MM:SS, H:MM:SS, MM:SS, or M:SS (H = hours,
        M = minutes, S = seconds). If an integer is provided (no colon
        present), the value is assumed to be in seconds. If one colon is
        present, the number to the left is assumed to be minutes, and the
        number to the right is assumed to be seconds. If more than two colons
        are present, the numbers farthest to the right are ignored.

        :param itunes_duration: Duration of the podcast episode.
        :returns: Duration of the podcast episode.
        '''
        if itunes_duration is not None:
            itunes_duration = str(itunes_duration)
            if len(itunes_duration.split(':')) > 3 or \
                    itunes_duration.lstrip('0123456789:') != '':
                raise ValueError('Invalid duration format')
            self.__itunes_duration = itunes_duration
        return self.__itunes_duration

    def itunes_explicit(self, itunes_explicit=None):
        '''Get or the the itunes:explicit value of the podcast episode. This
        tag should be used to indicate whether your podcast episode contains
        explicit material. The three values for this tag are "yes", "no", and
        "clean".

        If you populate this tag with "yes", an "explicit" parental advisory
        graphic will appear next to your podcast artwork on the iTunes Store
        and in the Name column in iTunes. If the value is "clean", the parental
        advisory type is considered Clean, meaning that no explicit language or
        adult content is included anywhere in the episodes, and a "clean"
        graphic will appear. If the explicit tag is present and has any other
        value (e.g., "no"), you see no indicator — blank is the default
        advisory type.

        :param itunes_explicit: If the podcast episode contains explicit
                                material.
        :returns: If the podcast episode contains explicit material.
        '''
        if itunes_explicit is not None:
            if itunes_explicit not in ('', 'yes', 'no', 'clean'):
                raise ValueError('Invalid value for explicit tag')
            self.__itunes_explicit = itunes_explicit
        return self.__itunes_explicit

    def itunes_is_closed_captioned(self, itunes_is_closed_captioned=None):
        '''Get or set the is_closed_captioned value of the podcast episode.
        This tag should be used if your podcast includes a video episode with
        embedded closed captioning support. The two values for this tag are
        "yes" and "no”.

        :param is_closed_captioned: If the episode has closed captioning
                                    support.
        :returns: If the episode has closed captioning support.
        '''
        if itunes_is_closed_captioned is not None:
            self.__itunes_is_closed_captioned = \
                    itunes_is_closed_captioned in ('yes', True)
        return self.__itunes_is_closed_captioned

    def itunes_order(self, itunes_order=None):
        '''Get or set the itunes:order value of the podcast episode. This tag
        can be used to override the default ordering of episodes on the store.

        This tag is used at an <item> level by populating with the number value
        in which you would like the episode to appear on the store. For
        example, if you would like an <item> to appear as the first episode in
        the podcast, you would populate the <itunes:order> tag with “1”. If
        conflicting order values are present in multiple episodes, the store
        will use default ordering (pubDate).

        To remove the order from the episode set the order to a value below
        zero.

        :param itunes_order: The order of the episode.
        :returns: The order of the episode.
        '''
        if itunes_order is not None:
            self.__itunes_order = int(itunes_order)
        return self.__itunes_order

    def itunes_subtitle(self, itunes_subtitle=None):
        '''Get or set the itunes:subtitle value for the podcast episode. The
        contents of this tag are shown in the Description column in iTunes. The
        subtitle displays best if it is only a few words long.

        :param itunes_subtitle: Subtitle of the podcast episode.
        :returns: Subtitle of the podcast episode.
        '''
        if itunes_subtitle is not None:
            self.__itunes_subtitle = itunes_subtitle
        return self.__itunes_subtitle

    def itunes_summary(self, itunes_summary=None):
        '''Get or set the itunes:summary value for the podcast episode. The
        contents of this tag are shown in a separate window that appears when
        the "circled i" in the Description column is clicked. It also appears
        on the iTunes page for your podcast. This field can be up to 4000
        characters. If <itunes:summary> is not included, the contents of the
        <description> tag are used.

        :param itunes_summary: Summary of the podcast episode.
        :returns: Summary of the podcast episode.
        '''
        if itunes_summary is not None:
            self.__itunes_summary = itunes_summary
        return self.__itunes_summary

    def itunes_season(self, itunes_season=None):
        '''Get or set the itunes:season value for the podcast episode.

        :param itunes_season: Season number of the podcast epiosode.
        :returns: Season number of the podcast episode.
        '''
        if itunes_season is not None:
            self.__itunes_season = int(itunes_season)
        return self.__itunes_season

    def itunes_episode(self, itunes_episode=None):
        '''Get or set the itunes:episode value for the podcast episode.

        :param itunes_season: Episode number of the podcast epiosode.
        :returns: Episode number of the podcast episode.
        '''
        if itunes_episode is not None:
            self.__itunes_episode = int(itunes_episode)
        return self.__itunes_episode

    def itunes_title(self, itunes_title=None):
        '''Get or set the itunes:title value for the podcast episode.

        An episode title specific for Apple Podcasts. Don’t specify the episode
        number or season number in this tag. Also, don’t repeat the title of
        your show within your episode title.

        :param itunes_title: Episode title specific for Apple Podcasts
        :returns: Title specific for Apple Podcast
        '''
        if itunes_title is not None:
            self.__itunes_title = itunes_title
        return self.__itunes_title

    def itunes_episode_type(self, itunes_episode_type=None):
        '''Get or set the itunes:episodeType value of the item. This tag should
        be used to indicate the episode type.
        The three values for this tag are "full", "trailer" and "bonus".

        If an episode is a trailer or bonus content, use this tag.

        Specify full when you are submitting the complete content of your show.
        Specify trailer when you are submitting a short, promotional piece of
        content that represents a preview of your current show.
        Specify bonus when you are submitting extra content for your show (for
        example, behind the scenes information or interviews with the cast) or
        cross-promotional content for another show.

        :param itunes_episode_type: The episode type
        :returns: type of the episode.
        '''
        if itunes_episode_type is not None:
            if itunes_episode_type not in ('full', 'trailer', 'bonus'):
                raise ValueError('Invalid value for episodeType tag')
            self.__itunes_episode_type = itunes_episode_type
        return self.__itunes_episode_type
