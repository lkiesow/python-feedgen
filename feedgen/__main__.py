# -*- coding: utf-8 -*-
'''
    feedgen
    ~~~~~~~

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
'''

from feedgen.feed import Podcast
import sys
import datetime
import pytz

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

    fg = Podcast()
    fg.title('Testfeed')
    fg.managingEditor('lkiesow@uos.de (Lars Kiesow)')
    fg.website(href='http://example.com')
    fg.copyright('cc-by')
    fg.description('This is a cool feed!')
    fg.language('de')
    fg.feed_url('http://example.com/feeds/myfeed.rss')
    fe = fg.add_episode()
    fe.id('http://lernfunk.de/_MEDIAID_123#1')
    fe.title('First Element')
    fe.summary('''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Tamen
            aberramus a proposito, et, ne longius, prorsus, inquam, Piso, si ista
            mala sunt, placet. Aut etiam, ut vestitum, sic sententiam habeas aliam
            domesticam, aliam forensem, ut in fronte ostentatio sit, intus veritas
            occultetur? Cum id fugiunt, re eadem defendunt, quae Peripatetici,
            verba <3.''', html=False)
    fe.link( href='http://example.com')
    fe.author( name='Lars Kiesow', email='lkiesow@uos.de' )

    if arg == 'rss':
        print_enc(fg.rss_str())
    elif arg == 'podcast':
        fg.itunes_author('Lars Kiesow')
        fg.itunes_category('Technology', 'Podcasting')
        fg.itunes_explicit('no')
        fg.itunes_complete('no')
        fg.itunes_new_feed_url('http://example.com/new-feed.rss')
        fg.itunes_owner('John Doe', 'john@example.com')
        fe.itunes_author('Lars Kiesow')
        fe.published(datetime.datetime(2014, 5, 17, 13, 37, 10, tzinfo=pytz.utc))
        print_enc(fg.rss_str())
    elif arg.endswith('rss'):
        fg.rss_file(arg, minimize=True)
