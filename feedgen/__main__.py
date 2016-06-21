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
    if sys.version_info[0] >= 3:
        print(s.decode('utf-8') if type(s) == type(b'') else s)
    else:
        print(s)



if __name__ == '__main__':
    if len(sys.argv) != 2 or not (
            sys.argv[1].endswith('rss') \
                    or sys.argv[1].endswith('podcast') ):
        print_enc ('Usage: %s ( <file>.rss | rss | podcast )' % \
                'python -m feedgen')
        print_enc ('')
        print_enc ('  rss              -- Generate RSS test output and print it to stdout.')
        print_enc ('  <file>.rss       -- Generate RSS test teed and write it to file.rss.')
        print_enc ('  podcast          -- Generate Podcast test output and print it to stdout.')
        print_enc ('')
        exit()

    arg = sys.argv[1]

    fg = FeedGenerator()
    fg.title('Testfeed')
    fg.author( {'name':'Lars Kiesow','email':'lkiesow@uos.de'} )
    fg.link( href='http://example.com')
    fg.category(term='test')
    fg.image('http://ex.com/logo.jpg')
    fg.copyright('cc-by')
    fg.description('This is a cool feed!')
    fg.language('de')
    fe = fg.add_entry()
    fe.guid('http://lernfunk.de/_MEDIAID_123#1')
    fe.title('First Element')
    fe.content('''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Tamen
            aberramus a proposito, et, ne longius, prorsus, inquam, Piso, si ista
            mala sunt, placet. Aut etiam, ut vestitum, sic sententiam habeas aliam
            domesticam, aliam forensem, ut in fronte ostentatio sit, intus veritas
            occultetur? Cum id fugiunt, re eadem defendunt, quae Peripatetici,
            verba.''')
    fe.description(u'Lorem ipsum dolor sit amet, consectetur adipiscing elit…')
    fe.link( href='http://example.com')
    fe.author( name='Lars Kiesow', email='lkiesow@uos.de' )

    if arg == 'rss':
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
    elif arg.endswith('rss'):
        fg.rss_file(arg)
