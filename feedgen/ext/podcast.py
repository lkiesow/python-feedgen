# -*- coding: utf-8 -*-
'''
    feedgen.ext.podcast
    ~~~~~~~~~~~~~~~~~~~

    Extends the FeedGenerator to produce podcasts.

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
'''

from feedgen.compat import string_types
from feedgen.ext.base import BaseExtension
from feedgen.util import ensure_format, xml_elem


class PodcastExtension(BaseExtension):
    '''FeedGenerator extension for podcasts.
    '''

    def __init__(self):
        # ITunes tags
        # http://www.apple.com/itunes/podcasts/specs.html#rss
        self.__itunes_author = None
        self.__itunes_block = None
        self.__itunes_category = None
        self.__itunes_image = None
        self.__itunes_explicit = None
        self.__itunes_complete = None
        self.__itunes_new_feed_url = None
        self.__itunes_owner = None
        self.__itunes_subtitle = None
        self.__itunes_summary = None
        self.__itunes_type = None
        # Spotify tags
        # http://www.spotify.com/ns/rss
        self.__spotify_limit = None
        self.__spotify_country_of_origin = None
        # Media tags
        # http://search.yahoo.com/mrss/
        self.__media_restriction = None

    def extend_ns(self):
        return {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
                'spotify': 'http://www.spotify.com/ns/rss',
                'media':'http://search.yahoo.com/mrss/'}

    def extend_rss(self, rss_feed):
        '''Extend an RSS feed root with set itunes fields.

        :returns: The feed root element.
        '''
        ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        SPOTIFY_NS = 'http://www.spotify.com/ns/rss'
        MEDIA_NS = 'http://search.yahoo.com/mrss/'

        channel = rss_feed[0]

        if self.__itunes_author:
            author = xml_elem('{%s}author' % ITUNES_NS, channel)
            author.text = self.__itunes_author

        if self.__itunes_block is not None:
            block = xml_elem('{%s}block' % ITUNES_NS, channel)
            block.text = 'yes' if self.__itunes_block else 'no'

        for c in self.__itunes_category or []:
            if not c.get('cat'):
                continue
            category = channel.find(
                    '{%s}category[@text="%s"]' % (ITUNES_NS, c.get('cat')))
            if category is None:
                category = xml_elem('{%s}category' % ITUNES_NS, channel)
                category.attrib['text'] = c.get('cat')

            if c.get('sub'):
                subcategory = xml_elem('{%s}category' % ITUNES_NS, category)
                subcategory.attrib['text'] = c.get('sub')

        if self.__itunes_image:
            image = xml_elem('{%s}image' % ITUNES_NS, channel)
            image.attrib['href'] = self.__itunes_image

        if self.__itunes_explicit in ('yes', 'no', 'clean'):
            explicit = xml_elem('{%s}explicit' % ITUNES_NS, channel)
            explicit.text = self.__itunes_explicit

        if self.__itunes_complete in ('yes', 'no'):
            complete = xml_elem('{%s}complete' % ITUNES_NS, channel)
            complete.text = self.__itunes_complete

        if self.__itunes_new_feed_url:
            new_feed_url = xml_elem('{%s}new-feed-url' % ITUNES_NS, channel)
            new_feed_url.text = self.__itunes_new_feed_url

        if self.__itunes_owner:
            owner = xml_elem('{%s}owner' % ITUNES_NS, channel)
            owner_name = xml_elem('{%s}name' % ITUNES_NS, owner)
            owner_name.text = self.__itunes_owner.get('name')
            owner_email = xml_elem('{%s}email' % ITUNES_NS, owner)
            owner_email.text = self.__itunes_owner.get('email')

        if self.__itunes_subtitle:
            subtitle = xml_elem('{%s}subtitle' % ITUNES_NS, channel)
            subtitle.text = self.__itunes_subtitle

        if self.__itunes_summary:
            summary = xml_elem('{%s}summary' % ITUNES_NS, channel)
            summary.text = self.__itunes_summary
        
        if self.__itunes_type:
            itunes_type = xml_elem('{%s}type' % ITUNES_NS, channel)
            itunes_type.text = self.__itunes_type
        
        if self.__spotify_limit:
            limit = xml_elem('{%s}limit' % SPOTIFY_NS, channel)
            limit.attrib['recentCount'] = self.__spotify_limit
        
        if self.__spotify_country_of_origin:
            countries = xml_elem('{%s}countryOfOrigin' % SPOTIFY_NS, channel)
            countries.text(self.__spotify_country_of_origin)
        
        if self.__media_restriction:
            restriction = xml_elem('{%s}restriction' % MEDIA_NS, channel)
            restriction.attrib['type'] = 'country'
            restriction.attrib['relationship'] = 'allow'
            restriction.text(self.__media_restriction)

        return rss_feed

    def itunes_author(self, itunes_author=None):
        '''Get or set the itunes:author. The content of this tag is shown in
        the Artist column in iTunes. If the tag is not present, iTunes uses the
        contents of the <author> tag. If <itunes:author> is not present at the
        feed level, iTunes will use the contents of <managingEditor>.

        :param itunes_author: The author of the podcast.
        :returns: The author of the podcast.
        '''
        if itunes_author is not None:
            self.__itunes_author = itunes_author
        return self.__itunes_author

    def itunes_block(self, itunes_block=None):
        '''Get or set the ITunes block attribute. Use this to prevent the
        entire podcast from appearing in the iTunes podcast directory.

        :param itunes_block: Block the podcast.
        :returns: If the podcast is blocked.
        '''
        if itunes_block is not None:
            self.__itunes_block = itunes_block
        return self.__itunes_block

    def itunes_category(self, itunes_category=None, replace=False, **kwargs):
        '''Get or set the ITunes category which appears in the category column
        and in iTunes Store Browser.

        The (sub-)category has to be one from the values defined at
        http://www.apple.com/itunes/podcasts/specs.html#categories

        This method can be called with:

        - the fields of an itunes_category as keyword arguments
        - the fields of an itunes_category as a dictionary
        - a list of dictionaries containing the itunes_category fields

        An itunes_category has the following fields:

        - *cat* name for a category.
        - *sub* name for a subcategory, child of category

        If a podcast has more than one subcategory from the same category, the
        category is called more than once.

        Likei the parameter::

            [{"cat":"Arts","sub":"Design"},{"cat":"Arts","sub":"Food"}]

        …would become::

            <itunes:category text="Arts">
                <itunes:category text="Design"/>
                <itunes:category text="Food"/>
            </itunes:category>


        :param itunes_category: Dictionary or list of dictionaries with
                                itunes_category data.
        :param replace: Add or replace old data.
        :returns: List of itunes_categories as dictionaries.

        ---

        **Important note about deprecated parameter syntax:** Old version of
        the feedgen did only support one category plus one subcategory which
        would be passed to this ducntion as first two parameters. For
        compatibility reasons, this still works but should not be used any may
        be removed at any time.
        '''
        # Ensure old API still works for now. Note that the API is deprecated
        # and this fallback may be removed at any time.
        if isinstance(itunes_category, string_types):
            itunes_category = {'cat': itunes_category}
            if replace:
                itunes_category['sub'] = replace
            replace = True
        if itunes_category is None and kwargs:
            itunes_category = kwargs
        if itunes_category is not None:
            if replace or self.__itunes_category is None:
                self.__itunes_category = []
            self.__itunes_category += ensure_format(itunes_category,
                                                    set(['cat', 'sub']),
                                                    set(['cat']))
        return self.__itunes_category

    def itunes_image(self, itunes_image=None):
        '''Get or set the image for the podcast. This tag specifies the artwork
        for your podcast. Put the URL to the image in the href attribute.
        iTunes prefers square .jpg images that are at least 1400x1400 pixels,
        which is different from what is specified for the standard RSS image
        tag. In order for a podcast to be eligible for an iTunes Store feature,
        the accompanying image must be at least 1400x1400 pixels.

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
                ValueError('Image file must be png or jpg')
        return self.__itunes_image

    def itunes_explicit(self, itunes_explicit=None):
        '''Get or the the itunes:explicit value of the podcast. This tag should
        be used to indicate whether your podcast contains explicit material.
        The three values for this tag are "yes", "no", and "clean".

        If you populate this tag with "yes", an "explicit" parental advisory
        graphic will appear next to your podcast artwork on the iTunes Store
        and in the Name column in iTunes. If the value is "clean", the parental
        advisory type is considered Clean, meaning that no explicit language or
        adult content is included anywhere in the episodes, and a "clean"
        graphic will appear. If the explicit tag is present and has any other
        value (e.g., "no"), you see no indicator — blank is the default
        advisory type.

        :param itunes_explicit: If the podcast contains explicit material.
        :returns: If the podcast contains explicit material.
        '''
        if itunes_explicit is not None:
            if itunes_explicit not in ('', 'yes', 'no', 'clean'):
                raise ValueError('Invalid value for explicit tag')
            self.__itunes_explicit = itunes_explicit
        return self.__itunes_explicit

    def itunes_complete(self, itunes_complete=None):
        '''Get or set the itunes:complete value of the podcast. This tag can be
        used to indicate the completion of a podcast.

        If you populate this tag with "yes", you are indicating that no more
        episodes will be added to the podcast. If the <itunes:complete> tag is
        present and has any other value (e.g. “no”), it will have no effect on
        the podcast.

        :param itunes_complete: If the podcast is complete.
        :returns: If the podcast is complete.
        '''
        if itunes_complete is not None:
            if itunes_complete not in ('yes', 'no', '', True, False):
                raise ValueError('Invalid value for complete tag')
            if itunes_complete is True:
                itunes_complete = 'yes'
            if itunes_complete is False:
                itunes_complete = 'no'
            self.__itunes_complete = itunes_complete
        return self.__itunes_complete

    def itunes_new_feed_url(self, itunes_new_feed_url=None):
        '''Get or set the new-feed-url property of the podcast. This tag allows
        you to change the URL where the podcast feed is located

        After adding the tag to your old feed, you should maintain the old feed
        for 48 hours before retiring it. At that point, iTunes will have
        updated the directory with the new feed URL.

        :param itunes_new_feed_url: New feed URL.
        :returns: New feed URL.
        '''
        if itunes_new_feed_url is not None:
            self.__itunes_new_feed_url = itunes_new_feed_url
        return self.__itunes_new_feed_url

    def itunes_owner(self, name=None, email=None):
        '''Get or set the itunes:owner of the podcast. This tag contains
        information that will be used to contact the owner of the podcast for
        communication specifically about the podcast. It will not be publicly
        displayed.

        :param itunes_owner: The owner of the feed.
        :returns: Data of the owner of the feed.
        '''
        if name is not None:
            if name and email:
                self.__itunes_owner = {'name': name, 'email': email}
            elif not name and not email:
                self.__itunes_owner = None
            else:
                raise ValueError('Both name and email have to be set.')
        return self.__itunes_owner

    def itunes_subtitle(self, itunes_subtitle=None):
        '''Get or set the itunes:subtitle value for the podcast. The contents of
        this tag are shown in the Description column in iTunes. The subtitle
        displays best if it is only a few words long.

        :param itunes_subtitle: Subtitle of the podcast.
        :returns: Subtitle of the podcast.
        '''
        if itunes_subtitle is not None:
            self.__itunes_subtitle = itunes_subtitle
        return self.__itunes_subtitle

    def itunes_summary(self, itunes_summary=None):
        '''Get or set the itunes:summary value for the podcast. The contents of
        this tag are shown in a separate window that appears when the "circled
        i" in the Description column is clicked. It also appears on the iTunes
        page for your podcast. This field can be up to 4000 characters. If
        `<itunes:summary>` is not included, the contents of the <description>
        tag are used.

        :param itunes_summary: Summary of the podcast.
        :returns: Summary of the podcast.
        '''
        if itunes_summary is not None:
            self.__itunes_summary = itunes_summary
        return self.__itunes_summary
    
    def itunes_type(self, itunes_type=None):
        '''Get or set the itunes:type value for the podcast. “episodic” for
        non-chronological episodes that will behave as they have for years and
        download the latest episode, or “serial” for chronological 0..1 episodes
        that should be consumed oldest to newest.

        :param itunes_type: The chronology of the podcast's episodes.
        :returns: The chronology of the podcast's epiodes.
        '''
        if itunes_type is not None:
            if itunes_type not in ['episodic','serial']:
                raise ValueError('Invalid value for itunes:type tag')
            self.__itunes_type = itunes_type
        return self.__itunes_type

    def spotify_limit(self, spotify_limit=None):
        '''Get or set the spotify:limit value for the podcast. If specified at
        most this number of episodes appear in the client, using the most recent
        episodes.

        :param spotify_limit: Number of latest episodes to show.
        :returns: Number of latest episodes to show.
        '''
        if spotify_limit is not None:
            if (isinstance(spotify_limit, str) and spotify_limit.is_digit()) or isinstance(spotify_limit, int): 
                self.__spotify_limit = spotify_limit
            else:
                raise ValueError('Invalid value for spotify:limit tag')
        return self.__spotify_limit

    def spotify_country_of_origin(self, spotify_country_of_origin=None):
        '''Get or set the spotify:countryOfOrigin value for the podcast. country of
        origin defines the intended market/territory where the podcast is relevant
        to the consumer. This is defined as a space separated list of ISO 3166
        country codes ranked in order of priority from most relevant to least
        relevant. Podcasts with a narrow list of countries will have a higher
        potential reaching their target audiences compared to podcasts with
        wide definitions. Podcasts omitting this element entirely will be
        defined as 'global' and not having a target market/territory.

        :param spotify_country_of_origin: Space-separated relevant country codes.
        :returns: Space-separated relevant country codes.
        '''
        if spotify_country_of_origin is not None:
            self.__spotify_country_of_origin = spotify_country_of_origin
        return self.__spotify_country_of_origin

    def media_restriction(self, media_restriction=None):
        '''Get or set the media:restriction value for the podcast. Restriction
        restricts availability of the podcast/show using a allowlist of space
        separated ISO 3166 country codes. The podcast will be published in the
        countries specified. If the restriction element is fully absent the
        content is considered available in all regions. Spotify currently only
        supports relationship="allow" and type="country".

        :param media_restriction: Allowed regions.
        :returns: Allowed regions.
        '''

        if media_restriction is not None:
            self.__media_restriction = media_restriction
        return self.__media_restriction

    _itunes_categories = {
            'Arts': [
                'Design', 'Fashion & Beauty', 'Food', 'Literature',
                'Performing Arts', 'Visual Arts'],
            'Business': [
                'Business News', 'Careers', 'Investing',
                'Management & Marketing', 'Shopping'],
            'Comedy': [],
            'Education': [
                'Education', 'Education Technology', 'Higher Education',
                'K-12', 'Language Courses', 'Training'],
            'Games & Hobbies': [
                'Automotive', 'Aviation', 'Hobbies', 'Other Games',
                'Video Games'],
            'Government & Organizations': [
                'Local', 'National', 'Non-Profit', 'Regional'],
            'Health': [
                'Alternative Health', 'Fitness & Nutrition', 'Self-Help',
                'Sexuality'],
            'Kids & Family': [],
            'Music': [],
            'News & Politics': [],
            'Religion & Spirituality': [
                'Buddhism', 'Christianity', 'Hinduism', 'Islam', 'Judaism',
                'Other', 'Spirituality'],
            'Science & Medicine': [
                'Medicine', 'Natural Sciences', 'Social Sciences'],
            'Society & Culture': [
                'History', 'Personal Journals', 'Philosophy',
                'Places & Travel'],
            'Sports & Recreation': [
                'Amateur', 'College & High School', 'Outdoor', 'Professional'],
            'Technology': [
                'Gadgets', 'Tech News', 'Podcasting', 'Software How-To'],
            'TV & Film': []}
