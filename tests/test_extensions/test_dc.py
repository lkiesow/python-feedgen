import unittest

from feedgen.feed import FeedGenerator


class TestExtensionDc(unittest.TestCase):

    def setUp(self):
        self.fg = FeedGenerator()
        self.fg.load_extension('dc')
        self.fg.title('title')
        self.fg.link(href='http://example.com', rel='self')
        self.fg.description('description')

    def test_entryLoadExtension(self):
        fe = self.fg.add_item()
        try:
            fe.load_extension('dc')
        except ImportError:
            pass  # Extension already loaded

    def test_elements(self):
        for method in dir(self.fg.dc):
            if method.startswith('dc_'):
                m = getattr(self.fg.dc, method)
                m(method)
                assert m() == [method]

        self.fg.id('123')
        assert self.fg.atom_str()
        assert self.fg.rss_str()
