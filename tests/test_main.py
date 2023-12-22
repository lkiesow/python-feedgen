# -*- coding: utf-8 -*-

'''
Tests for feedgen main
'''

import os
import sys
import tempfile
import unittest

from feedgen import __main__


class TestSequenceFunctions(unittest.TestCase):

    def test_usage(self):
        sys.argv = ['feedgen']
        with self.assertRaises(SystemExit) as e:
            __main__.main()
        self.assertEqual(e.exception.code, None)

    def test_feed(self):
        for ftype in 'rss', 'atom', 'podcast', 'torrent', 'dc.rss', \
                     'dc.atom', 'syndication.rss', 'syndication.atom':
            sys.argv = ['feedgen', ftype]
            __main__.main()

    def test_file(self):
        for extemsion in '.atom', '.rss':
            fh, filename = tempfile.mkstemp(extemsion)
            sys.argv = ['feedgen', filename]
            try:
                __main__.main()
            finally:
                os.close(fh)
                os.remove(filename)
