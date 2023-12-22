# -*- coding: utf-8 -*-

"""
Tests for a basic entry

These are test cases for a basic entry.
"""

import unittest

from feedgen.feed import FeedGenerator


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        fg = FeedGenerator()
        self.feedId = 'http://example.com'
        self.title = 'Some Testfeed'

        fg.id(self.feedId)
        fg.title(self.title)
        fg.link(href='http://lkiesow.de', rel='alternate')[0]
        fg.description('...')

        fe = fg.add_entry()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The First Episode')
        fe.content(u'…')

        # Use also the different name add_item
        fe = fg.add_item()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Second Episode')
        fe.content(u'…')

        fe = fg.add_entry()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Third Episode')
        fe.content(u'…')

        self.fg = fg

    def test_setEntries(self):
        fg2 = FeedGenerator()
        fg2.entry(self.fg.entry())
        self.assertEqual(len(fg2.entry()), 3)
        self.assertEqual(self.fg.entry(), fg2.entry())

    def test_loadExtension(self):
        fe = self.fg.add_item()
        fe.id('1')
        fe.title(u'…')
        fe.content(u'…')
        fe.load_extension('base')
        self.assertTrue(fe.base)
        self.assertTrue(self.fg.atom_str())

    def test_checkEntryNumbers(self):
        fg = self.fg
        self.assertEqual(len(fg.entry()), 3)

    def test_TestEntryItems(self):
        fe = self.fg.add_item()
        fe.title('qwe')
        self.assertEqual(fe.title(), 'qwe')
        author = fe.author(email='ldoe@example.com')[0]
        self.assertFalse(author.get('name'))
        self.assertEqual(author.get('email'), 'ldoe@example.com')
        author = fe.author(name='John Doe', email='jdoe@example.com',
                           replace=True)[0]
        self.assertEqual(author.get('name'), 'John Doe')
        self.assertEqual(author.get('email'), 'jdoe@example.com')
        contributor = fe.contributor(name='John Doe', email='jdoe@ex.com')[0]
        self.assertEqual(contributor, fe.contributor()[0])
        self.assertEqual(contributor.get('name'), 'John Doe')
        self.assertEqual(contributor.get('email'), 'jdoe@ex.com')
        link = fe.link(href='http://lkiesow.de', rel='alternate')[0]
        self.assertEqual(link, fe.link()[0])
        self.assertEqual(link.get('href'), 'http://lkiesow.de')
        self.assertEqual(link.get('rel'), 'alternate')
        fe.guid('123')
        self.assertEqual(fe.guid().get('guid'), '123')
        fe.updated('2017-02-05 13:26:58+01:00')
        self.assertEqual(fe.updated().year, 2017)
        fe.summary('asdf')
        self.assertEqual(fe.summary(), {'summary': 'asdf'})
        fe.description('asdfx')
        self.assertEqual(fe.description(), 'asdfx')
        fe.pubDate('2017-02-05 13:26:58+01:00')
        self.assertEqual(fe.pubDate().year, 2017)
        fe.rights('asdfx')
        self.assertEqual(fe.rights(), 'asdfx')
        source = fe.source(url='https://example.com', title='Test')
        self.assertEqual(source.get('title'), 'Test')
        self.assertEqual(source.get('url'), 'https://example.com')
        fe.comments('asdfx')
        self.assertEqual(fe.comments(), 'asdfx')
        fe.enclosure(url='http://lkiesow.de', type='text/plain', length='1')
        self.assertEqual(fe.enclosure().get('url'), 'http://lkiesow.de')
        fe.ttl(8)
        self.assertEqual(fe.ttl(), 8)

        self.fg.rss_str()
        self.fg.atom_str()

    def test_checkItemNumbers(self):
        fg = self.fg
        self.assertEqual(len(fg.item()), 3)

    def test_checkEntryContent(self):
        fg = self.fg
        self.assertTrue(fg.entry())

    def test_removeEntryByIndex(self):
        fg = FeedGenerator()
        self.feedId = 'http://example.com'
        self.title = 'Some Testfeed'

        fe = fg.add_entry()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Third Episode')
        self.assertEqual(len(fg.entry()), 1)
        fg.remove_entry(0)
        self.assertEqual(len(fg.entry()), 0)

    def test_removeEntryByEntry(self):
        fg = FeedGenerator()
        self.feedId = 'http://example.com'
        self.title = 'Some Testfeed'

        fe = fg.add_entry()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('The Third Episode')

        self.assertEqual(len(fg.entry()), 1)
        fg.remove_entry(fe)
        self.assertEqual(len(fg.entry()), 0)

    def test_categoryHasDomain(self):
        fg = FeedGenerator()
        fg.title('some title')
        fg.link(href='http://www.dontcare.com', rel='alternate')
        fg.description('description')
        fe = fg.add_entry()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title('some title')
        fe.category([
             {'term': 'category',
              'scheme': 'http://somedomain.com/category',
              'label': 'Category',
              }])

        result = fg.rss_str()
        self.assertIn(b'domain="http://somedomain.com/category"', result)

    def test_content_cdata_type(self):
        fg = FeedGenerator()
        fg.title('some title')
        fg.id('http://lernfunk.de/media/654322/1')
        fe = fg.add_entry()
        fe.id('http://lernfunk.de/media/654322/1')
        fe.title('some title')
        fe.content('content', type='CDATA')
        result = fg.atom_str()
        expected = b'<content type="CDATA"><![CDATA[content]]></content>'
        self.assertIn(expected, result)

    def test_summary_html_type(self):
        fg = FeedGenerator()
        fg.title('some title')
        fg.id('http://lernfunk.de/media/654322/1')
        fe = fg.add_entry()
        fe.id('http://lernfunk.de/media/654322/1')
        fe.title('some title')
        fe.link(href='http://lernfunk.de/media/654322/1')
        fe.summary('<p>summary</p>', type='html')
        result = fg.atom_str()
        expected = b'<summary type="html">&lt;p&gt;summary&lt;/p&gt;</summary>'
        self.assertIn(expected, result)
