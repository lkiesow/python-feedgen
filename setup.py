#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import feedgen.version

setup(
		name = 'feedgen',
		packages = ['feedgen', 'feedgen/ext'],
		version = feedgen.version.version_full_str,
		description = 'Feed Generator (ATOM, RSS, Podcasts)',
		author = 'Lars Kiesow',
		author_email = 'lkiesow@uos.de',
		url = 'http://lkiesow.github.io/python-feedgen',
		keywords = ['feed','ATOM','RSS','podcast'],
		license = 'FreeBSD and LGPLv3+',
		install_requires = ['lxml', 'dateutils'],
		classifiers = [
			'Development Status :: 4 - Beta',
			'Development Status :: 5 - Production/Stable',
			'Intended Audience :: Developers',
			'Intended Audience :: Information Technology',
			'Intended Audience :: Science/Research',
			'License :: OSI Approved :: BSD License',
			'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
			'Natural Language :: English',
			'Operating System :: OS Independent',
			'Programming Language :: Python',
			'Programming Language :: Python :: 2',
			'Topic :: Communications',
			'Topic :: Internet',
			'Topic :: Text Processing',
			'Topic :: Text Processing :: Markup',
			'Topic :: Text Processing :: Markup :: XML'
			],
		long_description = '''\
Feedgenerator
=============

This module can be used to generate web feeds in both ATOM and RSS format. It
has support for extensions. Included is for example an extension to produce
Podcasts.

It is licensed under the terms of both, the FreeBSD license and the LGPLv3+.
Choose the one which is more convenient for you. For more details have a look
at license.bsd and license.lgpl.
'''
)
