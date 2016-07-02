# -*- coding: utf-8 -*-
'''
    feedgen
    ~~~~~~~

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
'''

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


def main():
    """Create an example podcast and print it or save it to a file."""
    # There must be exactly one argument, and it is must end with rss
    if len(sys.argv) != 2 or not (
            sys.argv[1].endswith('rss')):
        # Invalid usage, print help message
        # print_enc is just a custom function which functions like print,
        # except it deals with byte arrays properly.
        print_enc ('Usage: %s ( <file>.rss | rss )' % \
                'python -m feedgen')
        print_enc ('')
        print_enc ('  rss              -- Generate RSS test output and print it to stdout.')
        print_enc ('  <file>.rss       -- Generate RSS test teed and write it to file.rss.')
        print_enc ('')
        exit()

    # Remember what type of feed the user wants
    arg = sys.argv[1]

    from feedgen.feed import Podcast
    from feedgen.person import Person
    from feedgen.media import Media
    # Initialize the feed
    p = Podcast()
    p.name('Testfeed')
    p.authors.append(Person("Lars Kiesow", "lkiesow@uos.de"))
    p.website(href='http://example.com')
    p.copyright('cc-by')
    p.description('This is a cool feed!')
    p.language('de')
    p.feed_url('http://example.com/feeds/myfeed.rss')
    p.itunes_category('Technology', 'Podcasting')
    p.itunes_explicit('no')
    p.itunes_complete('no')
    p.itunes_new_feed_url('http://example.com/new-feed.rss')
    p.itunes_owner(Person('John Doe', 'john@example.com'))

    e1 = p.add_episode()
    e1.id('http://lernfunk.de/_MEDIAID_123#1')
    e1.title('First Element')
    e1.summary('''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Tamen
            aberramus a proposito, et, ne longius, prorsus, inquam, Piso, si ista
            mala sunt, placet. Aut etiam, ut vestitum, sic sententiam habeas aliam
            domesticam, aliam forensem, ut in fronte ostentatio sit, intus veritas
            occultetur? Cum id fugiunt, re eadem defendunt, quae Peripatetici,
            verba <3.''', html=False)
    e1.link(href='http://example.com')
    e1.authors = [Person('Lars Kiesow', 'lkiesow@uos.de')]
    e1.published(datetime.datetime(2014, 5, 17, 13, 37, 10, tzinfo=pytz.utc))
    e1.enclosure(Media("http://example.com/episodes/loremipsum.mp3", 454599964))

    # Should we just print out, or write to file?
    if arg == 'rss':
        # Print
        print_enc(p.rss_str())
    elif arg.endswith('rss'):
        # Write to file
        p.rss_file(arg, minimize=True)

if __name__ == '__main__':
    main()
