# -*- coding: utf-8 -*-

"""
Tests for a basic feed

These are test cases for a basic feed.
A basic feed does not contain entries so far.
"""

import os
import tempfile
import unittest

from lxml import etree

from feedgen.ext.dc import DcEntryExtension, DcExtension
from feedgen.feed import FeedGenerator


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):

        fg = FeedGenerator()

        self.nsAtom = "http://www.w3.org/2005/Atom"
        self.nsRss = "http://purl.org/rss/1.0/modules/content/"

        self.feedId = 'http://lernfunk.de/media/654321'
        self.title = 'Some Testfeed'

        self.authorName = 'John Doe'
        self.authorMail = 'john@example.de'
        self.author = {'name': self.authorName, 'email': self.authorMail}

        self.linkHref = 'http://example.com'
        self.linkRel = 'alternate'

        self.logo = 'http://ex.com/logo.jpg'
        self.subtitle = 'This is a cool feed!'

        self.link2Href = 'http://larskiesow.de/test.atom'
        self.link2Rel = 'self'

        self.language = 'en'

        self.categoryTerm = 'This category term'
        self.categoryScheme = 'This category scheme'
        self.categoryLabel = 'This category label'

        self.cloudDomain = 'example.com'
        self.cloudPort = '4711'
        self.cloudPath = '/ws/example'
        self.cloudRegisterProcedure = 'registerProcedure'
        self.cloudProtocol = 'SOAP 1.1'

        self.icon = "http://example.com/icon.png"
        self.contributor = {'name': "Contributor Name",
                            'uri': "Contributor Uri",
                            'email': 'Contributor email'}
        self.copyright = "The copyright notice"
        self.docs = 'http://www.rssboard.org/rss-specification'
        self.managingEditor = 'mail@example.com'
        self.rating = '(PICS-1.1 "http://www.classify.org/safesurf/" ' + \
            '1 r (SS~~000 1))'
        self.skipDays = 'Tuesday'
        self.skipHours = 23

        self.textInputTitle = "Text input title"
        self.textInputDescription = "Text input description"
        self.textInputName = "Text input name"
        self.textInputLink = "Text input link"

        self.ttl = 900

        self.webMaster = 'webmaster@example.com'

        fg.id(self.feedId)
        fg.title(self.title)
        fg.author(self.author)
        fg.link(href=self.linkHref, rel=self.linkRel)
        fg.logo(self.logo)
        fg.subtitle(self.subtitle)
        fg.link(href=self.link2Href, rel=self.link2Rel)
        fg.language(self.language)
        fg.cloud(domain=self.cloudDomain, port=self.cloudPort,
                 path=self.cloudPath,
                 registerProcedure=self.cloudRegisterProcedure,
                 protocol=self.cloudProtocol)
        fg.icon(self.icon)
        fg.category(term=self.categoryTerm, scheme=self.categoryScheme,
                    label=self.categoryLabel)
        fg.contributor(self.contributor)
        fg.copyright(self.copyright)
        fg.docs(docs=self.docs)
        fg.managingEditor(self.managingEditor)
        fg.rating(self.rating)
        fg.skipDays(self.skipDays)
        fg.skipHours(self.skipHours)
        fg.textInput(title=self.textInputTitle,
                     description=self.textInputDescription,
                     name=self.textInputName, link=self.textInputLink)
        fg.ttl(self.ttl)
        fg.webMaster(self.webMaster)
        fg.updated('2017-02-05 13:26:58+01:00')
        fg.pubDate('2017-02-05 13:26:58+01:00')
        fg.generator('python-feedgen', 'x', uri='http://github.com/lkie...')
        fg.image(url=self.logo,
                 title=self.title,
                 link=self.link2Href,
                 width='123',
                 height='123',
                 description='Example Inage')

        self.fg = fg

    def test_baseFeed(self):
        fg = self.fg

        assert fg.id() == self.feedId
        assert fg.title() == self.title

        assert fg.author()[0]['name'] == self.authorName
        assert fg.author()[0]['email'] == self.authorMail

        assert fg.link()[0]['href'] == self.linkHref
        assert fg.link()[0]['rel'] == self.linkRel

        assert fg.logo() == self.logo
        assert fg.subtitle() == self.subtitle

        assert fg.link()[1]['href'] == self.link2Href
        assert fg.link()[1]['rel'] == self.link2Rel

        assert fg.language() == self.language

    def test_atomFeedFile(self):
        fg = self.fg
        fh, filename = tempfile.mkstemp()
        fg.atom_file(filename=filename, pretty=True, xml_declaration=False)

        with open(filename, "r") as myfile:
            atomString = myfile.read().replace('\n', '')

        self.checkAtomString(atomString)
        os.close(fh)
        os.remove(filename)

    def test_atomFeedString(self):
        fg = self.fg

        atomString = fg.atom_str(pretty=True, xml_declaration=False)
        self.checkAtomString(atomString)

    def test_rel_values_for_atom(self):
        values_for_rel = [
            'about', 'alternate', 'appendix', 'archives', 'author', 'bookmark',
            'canonical', 'chapter', 'collection', 'contents', 'copyright',
            'create-form', 'current', 'derivedfrom', 'describedby',
            'describes', 'disclosure', 'duplicate', 'edit', 'edit-form',
            'edit-media', 'enclosure', 'first', 'glossary', 'help', 'hosts',
            'hub', 'icon', 'index', 'item', 'last', 'latest-version',
            'license', 'lrdd', 'memento', 'monitor', 'monitor-group', 'next',
            'next-archive', 'nofollow', 'noreferrer', 'original', 'payment',
            'predecessor-version', 'prefetch', 'prev', 'preview', 'previous',
            'prev-archive', 'privacy-policy', 'profile', 'related', 'replies',
            'search', 'section', 'self', 'service', 'start', 'stylesheet',
            'subsection', 'successor-version', 'tag', 'terms-of-service',
            'timegate', 'timemap', 'type', 'up', 'version-history', 'via',
            'working-copy', 'working-copy-of']
        links = [{'href': '%s/%s' % (self.linkHref,
                                     val.replace('-', '_')), 'rel': val}
                 for val in values_for_rel]
        fg = self.fg
        fg.link(links, replace=True)
        atomString = fg.atom_str(pretty=True, xml_declaration=False)
        feed = etree.fromstring(atomString)
        nsAtom = self.nsAtom
        feed_links = feed.findall("{%s}link" % nsAtom)
        idx = 0
        assert len(links) == len(feed_links)
        while idx < len(values_for_rel):
            assert feed_links[idx].get('href') == links[idx]['href']
            assert feed_links[idx].get('rel') == links[idx]['rel']
            idx += 1

    def test_rel_values_for_rss(self):
        values_for_rel = [
            'about', 'alternate', 'appendix', 'archives', 'author', 'bookmark',
            'canonical', 'chapter', 'collection', 'contents', 'copyright',
            'create-form', 'current', 'derivedfrom', 'describedby',
            'describes', 'disclosure', 'duplicate', 'edit', 'edit-form',
            'edit-media', 'enclosure', 'first', 'glossary', 'help', 'hosts',
            'hub', 'icon', 'index', 'item', 'last', 'latest-version',
            'license', 'lrdd', 'memento', 'monitor', 'monitor-group', 'next',
            'next-archive', 'nofollow', 'noreferrer', 'original', 'payment',
            'predecessor-version', 'prefetch', 'prev', 'preview', 'previous',
            'prev-archive', 'privacy-policy', 'profile', 'related', 'replies',
            'search', 'section', 'self', 'service', 'start', 'stylesheet',
            'subsection', 'successor-version', 'tag', 'terms-of-service',
            'timegate', 'timemap', 'type', 'up', 'version-history', 'via',
            'working-copy', 'working-copy-of']
        links = [{'href': '%s/%s' % (self.linkHref,
                                     val.replace('-', '_')), 'rel': val}
                 for val in values_for_rel]
        fg = self.fg
        fg.link(links, replace=True)
        rssString = fg.rss_str(pretty=True, xml_declaration=False)
        feed = etree.fromstring(rssString)
        channel = feed.find("channel")
        nsAtom = self.nsAtom

        atom_links = channel.findall("{%s}link" % nsAtom)
        # rss feed only implements atom's 'self' link
        assert len(atom_links) == 1
        assert atom_links[0].get('href') == '%s/%s' % (self.linkHref, 'self')
        assert atom_links[0].get('rel') == 'self'

        rss_links = channel.findall('link')
        # RSS only needs one URL. We use the first link for RSS:
        assert len(rss_links) == 1
        assert rss_links[0].text == '%s/%s' % \
            (self.linkHref, 'working-copy-of'.replace('-', '_'))

    def checkAtomString(self, atomString):

        feed = etree.fromstring(atomString)

        nsAtom = self.nsAtom

        assert feed.find("{%s}title" % nsAtom).text == self.title
        assert feed.find("{%s}updated" % nsAtom).text is not None
        assert feed.find("{%s}id" % nsAtom).text == self.feedId
        assert feed.find("{%s}category" % nsAtom)\
            .get('term') == self.categoryTerm
        assert feed.find("{%s}category" % nsAtom)\
            .get('label') == self.categoryLabel
        assert feed.find("{%s}author" % nsAtom)\
            .find("{%s}name" % nsAtom).text == self.authorName
        assert feed.find("{%s}author" % nsAtom)\
            .find("{%s}email" % nsAtom).text == self.authorMail
        assert feed.findall("{%s}link" % nsAtom)[0]\
            .get('href') == self.linkHref
        assert feed.findall("{%s}link" % nsAtom)[0].get('rel') == self.linkRel
        assert feed.findall("{%s}link" % nsAtom)[1]\
            .get('href') == self.link2Href
        assert feed.findall("{%s}link" % nsAtom)[1].get('rel') == self.link2Rel
        assert feed.find("{%s}logo" % nsAtom).text == self.logo
        assert feed.find("{%s}icon" % nsAtom).text == self.icon
        assert feed.find("{%s}subtitle" % nsAtom).text == self.subtitle
        assert feed.find("{%s}contributor" % nsAtom)\
            .find("{%s}name" % nsAtom).text == self.contributor['name']
        assert feed.find("{%s}contributor" % nsAtom)\
            .find("{%s}email" % nsAtom).text == self.contributor['email']
        assert feed.find("{%s}contributor" % nsAtom)\
            .find("{%s}uri" % nsAtom).text == self.contributor['uri']
        assert feed.find("{%s}rights" % nsAtom).text == self.copyright

    def test_rssFeedFile(self):
        fg = self.fg
        _, filename = tempfile.mkstemp()
        fg.rss_file(filename=filename, pretty=True, xml_declaration=False)

        with open(filename, "r") as myfile:
            rssString = myfile.read().replace('\n', '')

        self.checkRssString(rssString)

    def test_rssFeedString(self):
        fg = self.fg
        rssString = fg.rss_str(pretty=True, xml_declaration=False)
        self.checkRssString(rssString)

    def test_loadPodcastExtension(self):
        fg = self.fg
        fg.add_entry()
        fg.load_extension('podcast', atom=True, rss=True)
        fg.add_entry()

    def test_loadDcExtension(self):
        fg = self.fg
        fg.add_entry()
        fg.load_extension('dc', atom=True, rss=True)
        fg.add_entry()

    def test_extensionAlreadyLoaded(self):
        fg = self.fg
        fg.load_extension('dc', atom=True, rss=True)
        with self.assertRaises(ImportError):
            fg.load_extension('dc')

    def test_registerCustomExtension(self):
        fg = self.fg
        fg.add_entry()
        fg.register_extension('dc', DcExtension, DcEntryExtension)
        fg.add_entry()

    def checkRssString(self, rssString):

        feed = etree.fromstring(rssString)
        nsAtom = self.nsAtom

        ch = feed.find("channel")
        assert ch is not None

        assert ch.find("title").text == self.title
        assert ch.find("description").text == self.subtitle
        assert ch.find("lastBuildDate").text is not None
        docs = "http://www.rssboard.org/rss-specification"
        assert ch.find("docs").text == docs
        assert ch.find("generator").text == "python-feedgen"
        assert ch.findall("{%s}link" % nsAtom)[0].get('href') == self.link2Href
        assert ch.findall("{%s}link" % nsAtom)[0].get('rel') == self.link2Rel
        assert ch.find("image").find("url").text == self.logo
        assert ch.find("image").find("title").text == self.title
        assert ch.find("image").find("link").text == self.link2Href
        assert ch.find("category").text == self.categoryLabel
        assert ch.find("cloud").get('domain') == self.cloudDomain
        assert ch.find("cloud").get('port') == self.cloudPort
        assert ch.find("cloud").get('path') == self.cloudPath
        assert ch.find("cloud").get('registerProcedure') == \
            self.cloudRegisterProcedure
        assert ch.find("cloud").get('protocol') == self.cloudProtocol
        assert ch.find("copyright").text == self.copyright
        assert ch.find("docs").text == self.docs
        assert ch.find("managingEditor").text == self.managingEditor
        assert ch.find("rating").text == self.rating
        assert ch.find("skipDays").find("day").text == self.skipDays
        assert int(ch.find("skipHours").find("hour").text) == self.skipHours
        assert ch.find("textInput").get('title') == self.textInputTitle
        assert ch.find("textInput").get('description') == \
            self.textInputDescription
        assert ch.find("textInput").get('name') == self.textInputName
        assert ch.find("textInput").get('link') == self.textInputLink
        assert int(ch.find("ttl").text) == self.ttl
        assert ch.find("webMaster").text == self.webMaster


if __name__ == '__main__':
    unittest.main()
