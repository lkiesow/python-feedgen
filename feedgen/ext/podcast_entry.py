# -*- coding: utf-8 -*-
'''
	feedgen.ext.podcast_entry
	~~~~~~~~~~~~~~~~~~~~~~~~~

	Extends the feedgen to produce podcasts.

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see license.* for more details.
'''

from lxml import etree
from feedgen.ext.base import BaseEntryExtension


class PodcastEntryExtension(BaseEntryExtension):
	'''FeedEntry extension for podcasts.
	'''


	def __init__(self):
		## ITunes tags
		# http://www.apple.com/itunes/podcasts/specs.html#rss
		self.__itunes_author              = None
		self.__itunes_block               = None
		self.__itunes_image               = None
		self.__itunes_duration            = None
		self.__itunes_explicit            = None
		self.__itunes_is_closed_captioned = None
		self.__itunes_order               = None
		self.__itunes_subtitle            = None
		self.__itunes_summary             = None


	def extend_rss(self, entry):
		'''Add additional fields to an RSS item.

		:param feed: The RSS item XML element to use.
		'''
		ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'

		if self.__itunes_author:
			author = etree.SubElement(entry, '{%s}author' % ITUNES_NS)
			author.text = self.__itunes_author

		if not self.__itunes_block is None:
			block = etree.SubElement(entry, '{%s}block' % ITUNES_NS)
			block.text = 'yes' if self.__itunes_block else 'no'

		if self.__itunes_image:
			image = etree.SubElement(entry, '{%s}image' % ITUNES_NS)
			image.attrib['href'] = self.__itunes_image

		if self.__itunes_duration:
			duration = etree.SubElement(entry, '{%s}duration' % ITUNES_NS)
			duration.text = self.__itunes_duration

		if self.__itunes_explicit in ('yes', 'no', 'clean'):
			explicit = etree.SubElement(entry, '{%s}explicit' % ITUNES_NS)
			explicit.text = self.__itunes_explicit

		if not self.__itunes_is_closed_captioned is None:
			is_closed_captioned = etree.SubElement(entry, '{%s}isClosedCaptioned' % ITUNES_NS)
			is_closed_captioned.text = 'yes' if self.__itunes_is_closed_captioned else 'no'

		if not self.__itunes_order is None and self.__itunes_order >= 0:
			order = etree.SubElement(entry, '{%s}order' % ITUNES_NS)
			order.text = str(self.__itunes_order)

		if self.__itunes_subtitle:
			subtitle = etree.SubElement(entry, '{%s}subtitle' % ITUNES_NS)
			subtitle.text = self.__itunes_subtitle

		if self.__itunes_summary:
			summary = etree.SubElement(entry, '{%s}summary' % ITUNES_NS)
			summary.text = self.__itunes_summary
		return entry


	def itunes_author(self, itunes_author=None):
		'''Get or set the itunes:author of the podcast episode. The content of
		this tag is shown in the Artist column in iTunes. If the tag is not
		present, iTunes uses the contents of the <author> tag. If <itunes:author>
		is not present at the feed level, iTunes will use the contents of
		<managingEditor>.

		:param itunes_author: The author of the podcast.
		:returns: The author of the podcast.
		'''
		if not itunes_author is None:
			self.__itunes_author = itunes_author
		return self.__itunes_author


	def itunes_block(self, itunes_block=None):
		'''Get or set the ITunes block attribute. Use this to prevent episodes
		from appearing in the iTunes podcast directory. 

		:param itunes_block: Block podcast episodes.
		:returns: If the podcast episode is blocked.
		'''
		if not itunes_block is None:
			self.__itunes_block = itunes_block
		return self.__itunes_block


	def itunes_image(self, itunes_image=None):
		'''Get or set the image for the podcast episode. This tag specifies the
		artwork for your podcast. Put the URL to the image in the href attribute.
		iTunes prefers square .jpg images that are at least 1400x1400 pixels,
		which is different from what is specified for the standard RSS image tag.
		In order for a podcast to be eligible for an iTunes Store feature, the
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


	def itunes_duration(self, itunes_duration=None):
		'''Get or set the duration of the podcast episode. The content of this
		tag is shown in the Time column in iTunes.

		The tag can be formatted HH:MM:SS, H:MM:SS, MM:SS, or M:SS (H = hours,
		M = minutes, S = seconds). If an integer is provided (no colon present),
		the value is assumed to be in seconds. If one colon is present, the
		number to the left is assumed to be minutes, and the number to the right
		is assumed to be seconds. If more than two colons are present, the
		numbers farthest to the right are ignored.

		:param itunes_duration: Duration of the podcast episode.
		:returns: Duration of the podcast episode.
		'''
		if not itunes_duration is None:
			itunes_duration = str(itunes_duration)
			if len(itunes_duration.split(':')) > 3 or \
					itunes_duration.lstrip('0123456789:') != '':
				ValueError('Invalid duration format')
			self.__itunes_duration = itunes_duration
		return self.itunes_duration


	def itunes_explicit(self, itunes_explicit=None):
		'''Get or the the itunes:explicit value of the podcast episode. This tag
		should be used to indicate whether your podcast episode contains explicit
		material. The three values for this tag are "yes", "no", and "clean".

		If you populate this tag with "yes", an "explicit" parental advisory
		graphic will appear next to your podcast artwork on the iTunes Store and
		in the Name column in iTunes. If the value is "clean", the parental
		advisory type is considered Clean, meaning that no explicit language or
		adult content is included anywhere in the episodes, and a "clean" graphic
		will appear. If the explicit tag is present and has any other value
		(e.g., "no"), you see no indicator — blank is the default advisory type.

		:param itunes_explicit: If the podcast episode contains explicit material.
		:returns: If the podcast episode contains explicit material.
		'''
		if not itunes_explicit is None:
			if not itunes_explicit in ('', 'yes', 'no', 'clean'):
				raise ValueError('Invalid value for explicit tag')
			self.__itunes_explicit = itunes_explicit
		return self.__itunes_explicit


	def itunes_is_closed_captioned(self, itunes_is_closed_captioned=None):
		'''Get or set the is_closed_captioned value of the podcast episode. This
		tag should be used if your podcast includes a video episode with embedded
		closed captioning support. The two values for this tag are "yes" and
		"no”.

		:param is_closed_captioned: If the episode has closed captioning support.
		:returns: If the episode has closed captioning support.
		'''
		if not itunes_is_closed_captioned is None:
			self.__itunes_is_closed_captioned = itunes_is_closed_captioned in ('yes', True)
		return self.__itunes_is_closed_captioned


	def itunes_order(self, itunes_order=None):
		'''Get or set the itunes:order value of the podcast episode. This tag can
		be used to override the default ordering of episodes on the store.

		This tag is used at an <item> level by populating with the number value
		in which you would like the episode to appear on the store. For example,
		if you would like an <item> to appear as the first episode in the
		podcast, you would populate the <itunes:order> tag with “1”. If
		conflicting order values are present in multiple episodes, the store will
		use default ordering (pubDate).

		To remove the order from the episode set the order to a value below zero.

		:param itunes_order: The order of the episode.
		:returns: The order of the episode.
		'''
		if not itunes_order is None:
			self.__itunes_order = int(itunes_order)
		return self.__itunes_order


	def itunes_subtitle(self, itunes_subtitle=None):
		'''Get or set the itunes:subtitle value for the podcast episode. The
		contents of this tag are shown in the Description column in iTunes. The
		subtitle displays best if it is only a few words long.

		:param itunes_subtitle: Subtitle of the podcast episode.
		:returns: Subtitle of the podcast episode.
		'''
		if not itunes_subtitle is None:
			self.__itunes_subtitle = itunes_subtitle
		return self.__itunes_subtitle


	def itunes_summary(self, itunes_summary=None):
		'''Get or set the itunes:summary value for the podcast episode. The
		contents of this tag are shown in a separate window that appears when the
		"circled i" in the Description column is clicked. It also appears on the
		iTunes page for your podcast. This field can be up to 4000 characters. If
		<itunes:summary> is not included, the contents of the <description> tag
		are used.

		:param itunes_summary: Summary of the podcast episode.
		:returns: Summary of the podcast episode.
		'''
		if not itunes_summary is None:
			self.__itunes_summary = itunes_summary
		return self.__itunes_summary
