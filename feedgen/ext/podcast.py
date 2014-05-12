# -*- coding: utf-8 -*-
'''
	feedgen.ext.podcast
	~~~~~~~~~~~~~~~~~~~

	Extends the FeedGenerator to produce podcasts.

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see license.* for more details.
'''

from lxml import etree
from feedgen.ext.base import BaseExtension


class PodcastExtension(BaseExtension):
	'''FeedGenerator extension for podcasts.
	'''


	def __init__(self):
		## ITunes tags
		# http://www.apple.com/itunes/podcasts/specs.html#rss
		self.__itunes_author       = None
		self.__itunes_block        = None
		self.__itunes_category     = None
		self.__itunes_image        = None
		self.__itunes_explicit     = None
		self.__itunes_complete     = None
		self.__itunes_new_feed_url = None
		self.__itunes_owner        = None
		self.__itunes_subtitle     = None
		self.__itunes_summary      = None


	def extend_ns(self):
		return {'itunes' : 'http://www.itunes.com/dtds/podcast-1.0.dtd'}


	def extend_rss(self, rss_feed):
		'''Extend an RSS feed root with set itunes fields.

		:returns: The feed root element.
		'''
		ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
		channel = rss_feed[0]

		if self.__itunes_author:
			author = etree.SubElement(channel, '{%s}author' % ITUNES_NS)
			author.text = self.__itunes_author

		if not self.__itunes_block is None:
			block = etree.SubElement(channel, '{%s}block' % ITUNES_NS)
			block.text = 'yes' if self.__itunes_block else 'no'

		if self.__itunes_category:
			category = etree.SubElement(channel, '{%s}category' % ITUNES_NS)
			category.attrib['text'] = self.__itunes_category['cat']
			if self.__itunes_category.get('sub'):
				subcategory = etree.SubElement(category, '{%s}category' % ITUNES_NS)
				subcategory.attrib['text'] = self.__itunes_category['sub']

		if self.__itunes_image:
			image = etree.SubElement(channel, '{%s}image' % ITUNES_NS)
			image.attrib['href'] = self.__itunes_image

		if self.__itunes_explicit in ('yes', 'no', 'clean'):
			explicit = etree.SubElement(channel, '{%s}explicit' % ITUNES_NS)
			explicit.text = self.__itunes_explicit

		if self.__itunes_complete in ('yes', 'no'):
			complete = etree.SubElement(channel, '{%s}complete' % ITUNES_NS)
			complete.text = self.__itunes_complete

		if self.__itunes_new_feed_url:
			new_feed_url = etree.SubElement(channel, '{%s}new-feed-url' % ITUNES_NS)
			new_feed_url.text = self.__itunes_new_feed_url

		if self.__itunes_owner:
			owner = etree.SubElement(channel, '{%s}owner' % ITUNES_NS)
			owner_name = etree.SubElement(owner, '{%s}name' % ITUNES_NS)
			owner_name.text = self.__itunes_owner.get('name')
			owner_email = etree.SubElement(owner, '{%s}email' % ITUNES_NS)
			owner_email.text = self.__itunes_owner.get('email')

		if self.__itunes_subtitle:
			subtitle = etree.SubElement(channel, '{%s}subtitle' % ITUNES_NS)
			subtitle.text = self.__itunes_subtitle

		if self.__itunes_summary:
			summary = etree.SubElement(channel, '{%s}summary' % ITUNES_NS)
			summary.text = self.__itunes_summary

		return rss_feed


	def itunes_author(self, itunes_author=None):
		'''Get or set the itunes:author. The content of this tag is shown in the
		Artist column in iTunes. If the tag is not present, iTunes uses the
		contents of the <author> tag. If <itunes:author> is not present at the
		feed level, iTunes will use the contents of <managingEditor>.

		:param itunes_author: The author of the podcast.
		:returns: The author of the podcast.
		'''
		if not itunes_author is None:
			self.__itunes_author = itunes_author
		return self.__itunes_author


	def itunes_block(self, itunes_block=None):
		'''Get or set the ITunes block attribute. Use this to prevent the entire
		podcast from appearing in the iTunes podcast directory.

		:param itunes_block: Block the podcast.
		:returns: If the podcast is blocked.
		'''
		if not itunes_block is None:
			self.__itunes_block = itunes_block
		return self.__itunes_block


	def itunes_category(self, itunes_category=None, itunes_subcategory=None):
		'''Get or set the ITunes category which appears in the category column
		and in iTunes Store Browser.

		The (sub-)category has to be one from the values defined at
		http://www.apple.com/itunes/podcasts/specs.html#categories

		:param itunes_category: Category of the podcast.
		:param itunes_subcategory: Subcategory of the podcast.
		:returns: Category data of the podcast.
		'''
		if not itunes_category is None:
			if not itunes_category in self._itunes_categories.keys():
				raise ValueError('Invalid category')
			cat = {'cat':itunes_category}
			if not itunes_subcategory is None:
				if not itunes_subcategory in self._itunes_categories[itunes_category]:
					raise ValueError('Invalid subcategory')
				cat['sub'] = itunes_subcategory
			self.__itunes_category = cat
		return self.__itunes_category


	def itunes_image(self, itunes_image=None):
		'''Get or set the image for the podcast. This tag specifies the artwork
		for your podcast. Put the URL to the image in the href attribute. iTunes
		prefers square .jpg images that are at least 1400x1400 pixels, which is
		different from what is specified for the standard RSS image tag. In order
		for a podcast to be eligible for an iTunes Store feature, the
		accompanying image must be at least 1400x1400 pixels.

		iTunes supports images in JPEG and PNG formats with an RGB color space
		(CMYK is not supported). The URL must end in ".jpg" or ".png". If the
		<itunes:image> tag is not present, iTunes will use the contents of the
		RSS image tag.

		If you change your podcast’s image, also change the file’s name. iTunes
		may not change the image if it checks your feed and the image URL is the
		same. The server hosting your cover art image must allow HTTP head
		requests for iTS to be able to automatically update your cover art.

		:param itunes_image: Image of the podcast.
		:returns: Image of the podcast.
		'''
		if not itunes_image is None:
			if not ( itunes_image.endswith('.jpg') or itunes_image.endswith('.png') ):
				ValueError('Image file must be png or jpg')
			self.__itunes_image = itunes_image
		return self.__itunes_image


	def itunes_explicit(self, itunes_explicit=None):
		'''Get or the the itunes:explicit value of the podcast. This tag should
		be used to indicate whether your podcast contains explicit material. The
		three values for this tag are "yes", "no", and "clean".

		If you populate this tag with "yes", an "explicit" parental advisory
		graphic will appear next to your podcast artwork on the iTunes Store and
		in the Name column in iTunes. If the value is "clean", the parental
		advisory type is considered Clean, meaning that no explicit language or
		adult content is included anywhere in the episodes, and a "clean" graphic
		will appear. If the explicit tag is present and has any other value
		(e.g., "no"), you see no indicator — blank is the default advisory type.

		:param itunes_explicit: If the podcast contains explicit material.
		:returns: If the podcast contains explicit material.
		'''
		if not itunes_explicit is None:
			if not itunes_explicit in ('', 'yes', 'no', 'clean'):
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
		if not itunes_complete is None:
			if not itunes_complete in ('yes', 'no', '', True, False):
				raise ValueError('Invalid value for complete tag')
			if itunes_complete == True:
				itunes_complete = 'yes'
			if itunes_complete == False:
				itunes_complete = 'no'
			self.__itunes_complete = itunes_complete
		return self.__itunes_complete


	def itunes_new_feed_url(self, itunes_new_feed_url=None):
		'''Get or set the new-feed-url property of the podcast. This tag allows
		you to change the URL where the podcast feed is located

		After adding the tag to your old feed, you should maintain the old feed
		for 48 hours before retiring it. At that point, iTunes will have updated
		the directory with the new feed URL.

		:param itunes_new_feed_url: New feed URL.
		:returns: New feed URL.
		'''
		if not itunes_new_feed_url is None:
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
		if not name is None:
			if name and email:
				self.__itunes_owner = {'name':name, 'email':email}
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
		if not itunes_subtitle is None:
			self.__itunes_subtitle = itunes_subtitle
		return self.__itunes_subtitle


	def itunes_summary(self, itunes_summary=None):
		'''Get or set the itunes:summary value for the podcast. The contents of
		this tag are shown in a separate window that appears when the "circled i"
		in the Description column is clicked. It also appears on the iTunes page
		for your podcast. This field can be up to 4000 characters. If
		<itunes:summary> is not included, the contents of the <description> tag
		are used.

		:param itunes_summary: Summary of the podcast.
		:returns: Summary of the podcast.
		'''
		if not itunes_summary is None:
			self.__itunes_summary = itunes_summary
		return self.__itunes_summary


	_itunes_categories = {
			'Arts': [ 'Design', 'Fashion & Beauty', 'Food', 'Literature',
				'Performing Arts', 'Visual Arts' ],
			'Business' : [ 'Business News', 'Careers', 'Investing',
				'Management & Marketing', 'Shopping' ],
			'Comedy' : [],
			'Education' : [ 'Education', 'Education Technology',
				'Higher Education', 'K-12', 'Language Courses', 'Training' ],
			'Games & Hobbies' : [ 'Automotive', 'Aviation', 'Hobbies',
				'Other Games', 'Video Games' ],
			'Government & Organizations' : [ 'Local', 'National', 'Non-Profit',
				'Regional' ],
			'Health' : [ 'Alternative Health', 'Fitness & Nutrition', 'Self-Help',
				'Sexuality' ],
			'Kids & Family' : [],
			'Music' : [],
			'News & Politics' : [],
			'Religion & Spirituality' : [ 'Buddhism', 'Christianity', 'Hinduism',
				'Islam', 'Judaism', 'Other', 'Spirituality' ],
			'Science & Medicine' : [ 'Medicine', 'Natural Sciences',
				'Social Sciences' ],
			'Society & Culture' : [ 'History', 'Personal Journals', 'Philosophy',
				'Places & Travel' ],
			'Sports & Recreation' : [ 'Amateur', 'College & High School',
				'Outdoor', 'Professional' ],
			'Technology' : [ 'Gadgets', 'Tech News', 'Podcasting',
				'Software How-To' ],
			'TV & Film' : []
			}
