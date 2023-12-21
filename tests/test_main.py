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
        try:
            __main__.main()
        except BaseException as e:
            assert e.code is None

    def test_feed(self):
        for ftype in 'rss', 'atom', 'podcast', 'torrent', 'dc.rss', \
                     'dc.atom', 'syndication.rss', 'syndication.atom':
            sys.argv = ['feedgen', ftype]
            try:
                __main__.main()
            except Exception:
                assert False

    def test_file(self):
        for extemsion in '.atom', '.rss':
            fh, filename = tempfile.mkstemp(extemsion)
            sys.argv = ['feedgen', filename]
            try:
                __main__.main()
            except Exception:
                assert False
            os.close(fh)
            os.remove(filename)
