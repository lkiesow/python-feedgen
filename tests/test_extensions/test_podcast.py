import unittest

from lxml import etree

from feedgen.feed import FeedGenerator


class TestExtensionPodcast(unittest.TestCase):

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('podcast')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_category_new(self):
        self.fg.podcast.itunes_category([{'cat': 'Technology',
                                          'sub': 'Podcasting'}])
        self.fg.podcast.itunes_explicit('no')
        self.fg.podcast.itunes_complete('no')
        self.fg.podcast.itunes_new_feed_url('http://example.com/new-feed.rss')
        self.fg.podcast.itunes_owner('John Doe', 'john@example.com')
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        root = etree.fromstring(self.fg.rss_str())
        cat = root.xpath('/rss/channel/itunes:category/@text', namespaces=ns)
        scat = root.xpath('/rss/channel/itunes:category/itunes:category/@text',
                          namespaces=ns)
        self.assertEqual(cat[0], 'Technology')
        self.assertEqual(scat[0], 'Podcasting')

    def test_category(self):
        self.fg.podcast.itunes_category('Technology', 'Podcasting')
        self.fg.podcast.itunes_explicit('no')
        self.fg.podcast.itunes_complete('no')
        self.fg.podcast.itunes_new_feed_url('http://example.com/new-feed.rss')
        self.fg.podcast.itunes_owner('John Doe', 'john@example.com')
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        root = etree.fromstring(self.fg.rss_str())
        cat = root.xpath('/rss/channel/itunes:category/@text', namespaces=ns)
        scat = root.xpath('/rss/channel/itunes:category/itunes:category/@text',
                          namespaces=ns)
        self.assertEqual(cat[0], 'Technology')
        self.assertEqual(scat[0], 'Podcasting')

    def test_podcastItems(self):
        fg = self.fg
        fg.podcast.itunes_author('Lars Kiesow')
        fg.podcast.itunes_block('x')
        fg.podcast.itunes_complete(False)
        fg.podcast.itunes_explicit('no')
        fg.podcast.itunes_image('x.png')
        fg.podcast.itunes_subtitle('x')
        fg.podcast.itunes_summary('x')
        fg.podcast.itunes_type('episodic')
        self.assertEqual(fg.podcast.itunes_author(), 'Lars Kiesow')
        self.assertEqual(fg.podcast.itunes_block(), 'x')
        self.assertEqual(fg.podcast.itunes_complete(), 'no')
        self.assertEqual(fg.podcast.itunes_explicit(), 'no')
        self.assertEqual(fg.podcast.itunes_image(), 'x.png')
        self.assertEqual(fg.podcast.itunes_subtitle(), 'x')
        self.assertEqual(fg.podcast.itunes_summary(), 'x')
        self.assertEqual(fg.podcast.itunes_type(), 'episodic')

        # Check that we have the item in the resulting XML
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        root = etree.fromstring(self.fg.rss_str())
        author = root.xpath('/rss/channel/itunes:author/text()', namespaces=ns)
        self.assertEqual(author, ['Lars Kiesow'])

    def test_podcastEntryItems(self):
        fe = self.fg.add_item()
        fe.title('y')
        fe.podcast.itunes_author('Lars Kiesow')
        fe.podcast.itunes_block('x')
        fe.podcast.itunes_duration('00:01:30')
        fe.podcast.itunes_explicit('no')
        fe.podcast.itunes_image('x.png')
        fe.podcast.itunes_is_closed_captioned('yes')
        fe.podcast.itunes_order(1)
        fe.podcast.itunes_subtitle('x')
        fe.podcast.itunes_summary('x')
        fe.podcast.itunes_season(1)
        fe.podcast.itunes_episode(1)
        fe.podcast.itunes_title('Podcast Title')
        fe.podcast.itunes_episode_type('full')
        self.assertEqual(fe.podcast.itunes_author(), 'Lars Kiesow')
        self.assertEqual(fe.podcast.itunes_block(), 'x')
        self.assertEqual(fe.podcast.itunes_duration(), '00:01:30')
        self.assertEqual(fe.podcast.itunes_explicit(), 'no')
        self.assertEqual(fe.podcast.itunes_image(), 'x.png')
        self.assertTrue(fe.podcast.itunes_is_closed_captioned())
        self.assertEqual(fe.podcast.itunes_order(), 1)
        self.assertEqual(fe.podcast.itunes_subtitle(), 'x')
        self.assertEqual(fe.podcast.itunes_summary(), 'x')
        self.assertEqual(fe.podcast.itunes_season(), 1)
        self.assertEqual(fe.podcast.itunes_episode(), 1)
        self.assertEqual(fe.podcast.itunes_title(), 'Podcast Title')
        self.assertEqual(fe.podcast.itunes_episode_type(), 'full')

        # Check that we have the item in the resulting XML
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        root = etree.fromstring(self.fg.rss_str())
        author = root.xpath('/rss/channel/item/itunes:author/text()',
                            namespaces=ns)
        self.assertEqual(author, ['Lars Kiesow'])
