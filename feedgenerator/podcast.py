#!/bin/env python
# -*- coding: utf-8 -*-
'''
	feedgenerator.podcast
	~~~~~~~~~~~~~~~~~~~~~

	Extends the feedgenerator to produce podcasts.

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see LICENSE for more details.
'''

from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from feedgenerator.feed import FeedGenerator
from feedgenerator.util import ensure_format


class PodcastGenerator(FeedGenerator):


	## ITunes tags
	# http://www.apple.com/itunes/podcasts/specs.html#rss
	__itunes_author       = None
	__itunes_block        = None
	__itunes_category     = None
	__itunes_image        = None
	__itunes_explicit     = None
	__itunes_complete     = None
	__itunes_new_feed_url = None




	def __create_podcast(self):
		'''Create an RSS feed xml structure containing all previously set fields.

		:returns: Tuple containing the feed root element and the element tree.
		'''
		rss_feed, _ = super(PodcastGenerator,self)._create_rss()
		# Replace the root element to add the itunes namespace
		ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
		feed = etree.Element('rss', version='2.0',
				nsmap={
					'atom'  :'http://www.w3.org/2005/Atom', 
					'itunes':ITUNES_NS} )
		feed[:] = rss_feed[:]
		channel = feed[0]
		doc     = etree.ElementTree(feed)

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

		if self.__itunes_explicit in ('yes', 'no', 'clean'):
			explicit = etree.SubElement(channel, '{%s}explicit' % ITUNES_NS)
			explicit.text = self.__itunes_explicit

		if self.__itunes_complete in ('yes', 'no'):
			complete = etree.SubElement(channel, '{%s}complete' % ITUNES_NS)
			complete.text = self.__itunes_complete

		if self.__itunes_new_feed_url:
			new_feed_url = etree.SubElement(channel, '{%s}new-feed-url' % ITUNES_NS)
			new_feed_url.text = self.__itunes_new_feed_url

		return feed, doc


	def podcast_str(self, pretty=False):
		'''Generates an RSS feed and returns the feed XML as string.
		
		:param pretty: If the feed should be split into multiple lines and
			properly indented.
		:returns: String representation of the RSS feed.
		'''
		feed, doc = self.__create_podcast()
		return etree.tostring(feed, pretty_print=pretty)


	def podcast_file(self, filename):
		'''Generates an RSS feed and write the resulting XML to a file.
		
		:param filename: Name of file to write.
		'''
		feed, doc = self.__create_podcast()
		with open(filename, 'w') as f:
			doc.write(f)


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
