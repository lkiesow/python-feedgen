#!/bin/env python
# -*- coding: utf-8 -*-
'''
	feedgenerator
	~~~~~~~~~~~~~

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see LICENSE for more details.
'''

from feedgenerator.feed import FeedGenerator
from feedgenerator.podcast import PodcastGenerator
import sys



if __name__ == '__main__':
	if len(sys.argv) != 2 or not ( 
			sys.argv[1].endswith('rss') \
					or sys.argv[1].endswith('atom') \
					or sys.argv[1].endswith('podcast') ):
		print 'Usage: %s ( <file>.atom | atom | <file>.rss | rss )' % \
				'pythom -m feedgenerator'
		print ''
		print '  atom        -- Generate ATOM test output and print it to stdout.'
		print '  rss         -- Generate RSS test output and print it to stdout.'
		print '  <file>.atom -- Generate ATOM test feed and write it to file.atom.'
		print '  <file>.rss  -- Generate RSS test teed and write it to file.rss.'
		print ''
		exit()

	arg = sys.argv[1]

	fg = PodcastGenerator() if arg.endswith('podcast') else FeedGenerator()
	fg.id('http://lernfunk.de/_MEDIAID_123')
	fg.title('Testfeed')
	fg.author( {'name':'Lars Kiesow','email':'lkiesow@uos.de'} )
	fg.link( href='http://example.com', rel='alternate' )
	fg.category(term='test')
	fg.contributor( name='Lars Kiesow', email='lkiesow@uos.de' )
	fg.contributor( name='John Doe', email='jdoe@example.com' )
	fg.icon('http://ex.com/icon.jpg')
	fg.logo('http://ex.com/logo.jpg')
	fg.rights('cc-by')
	fg.subtitle('This is a cool feed!')
	fg.link( href='http://larskiesow.de/test.atom', rel='self' )
	fg.language('de')
	fe = fg.add_entry()
	fe.id('http://lernfunk.de/_MEDIAID_123#1')
	fe.title('First Element')
	fe.content('''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Tamen
			aberramus a proposito, et, ne longius, prorsus, inquam, Piso, si ista
			mala sunt, placet. Aut etiam, ut vestitum, sic sententiam habeas aliam
			domesticam, aliam forensem, ut in fronte ostentatio sit, intus veritas
			occultetur? Cum id fugiunt, re eadem defendunt, quae Peripatetici,
			verba.''')
	fe.summary('Lorem ipsum dolor sit amet, consectetur adipiscing elit...')
	fe.link( href='http://example.com', rel='alternate' )
	fe.author( name='Lars Kiesow', email='lkiesow@uos.de' )

	if arg == 'atom':
		print fg.atom_str(pretty=True)
	elif arg == 'rss':
		print fg.rss_str(pretty=True)
	elif arg == 'podcast':
		fg.itunes_author('Lars Kiesow')
		fg.itunes_category('Technology', 'Podcasting')
		print fg.podcast_str(pretty=True)
	elif arg.endswith('atom'):
		fg.atom_file(arg)
	elif arg.endswith('rss'):
		fg.rss_file(arg)
