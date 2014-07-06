# -*- coding: utf-8 -*-
'''
	feedgen
	~~~~~~~

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see license.* for more details.
'''

from feedgen.feed import FeedGenerator
import sys

def print_enc(s):
	'''Print function compatible with both python2 and python3 accepting strings
	and byte arrays.
	'''
	print(s.decode('utf-8') if type(s) == type(b'') else s)



if __name__ == '__main__':
	if len(sys.argv) != 2 or not (
			sys.argv[1].endswith('rss') \
					or sys.argv[1].endswith('atom') \
					or sys.argv[1].endswith('podcast') ):
		print_enc ('Usage: %s ( <file>.atom | atom | <file>.rss | rss | podcast )' % \
				'python -m feedgen')
		print_enc ('')
		print_enc ('  atom        -- Generate ATOM test output and print it to stdout.')
		print_enc ('  rss         -- Generate RSS test output and print it to stdout.')
		print_enc ('  <file>.atom -- Generate ATOM test feed and write it to file.atom.')
		print_enc ('  <file>.rss  -- Generate RSS test teed and write it to file.rss.')
		print_enc ('  podcast     -- Generate Podcast test output and print it to stdout.')
		print_enc ('  dc.atom     -- Generate DC extension test output (atom format) and print it to stdout.')
		print_enc ('  dc.rss      -- Generate DC extension test output (rss format) and print it to stdout.')
		print_enc ('')
		exit()

	arg = sys.argv[1]

	fg = FeedGenerator()
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
	fe.summary(u'Lorem ipsum dolor sit amet, consectetur adipiscing elit…')
	fe.link( href='http://example.com', rel='alternate' )
	fe.author( name='Lars Kiesow', email='lkiesow@uos.de' )

	if arg == 'atom':
		print_enc (fg.atom_str(pretty=True))
	elif arg == 'rss':
		print_enc (fg.rss_str(pretty=True))
	elif arg == 'podcast':
		# Load the podcast extension. It will automatically be loaded for all
		# entries in the feed, too. Thus also for our “fe”.
		fg.load_extension('podcast')
		fg.podcast.itunes_author('Lars Kiesow')
		fg.podcast.itunes_category('Technology', 'Podcasting')
		fg.podcast.itunes_explicit('no')
		fg.podcast.itunes_complete('no')
		fg.podcast.itunes_new_feed_url('http://example.com/new-feed.rss')
		fg.podcast.itunes_owner('John Doe', 'john@example.com')
		fg.podcast.itunes_summary('Lorem ipsum dolor sit amet, ' + \
				'consectetur adipiscing elit. ' + \
				'Verba tu fingas et ea dicas, quae non sentias?')
		fe.podcast.itunes_author('Lars Kiesow')
		print_enc (fg.rss_str(pretty=True))

	elif arg == 'dc.atom':
		fg.load_extension('dc')
		fg.dc.dc_contributor('Lars Kiesow')
		fe.dc.dc_contributor('Lars Kiesow')
		print_enc (fg.atom_str(pretty=True))

	elif arg == 'dc.rss':
		fg.load_extension('dc')
		fg.dc.dc_contributor('Lars Kiesow')
		print_enc (fg.rss_str(pretty=True))

	elif arg.endswith('atom'):
		fg.atom_file(arg)

	elif arg.endswith('rss'):
		fg.rss_file(arg)
