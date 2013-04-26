#!/bin/env python
# -*- coding: utf-8 -*-
'''
	feedgenerator.util
	~~~~~~~~~~~~~~~~~~

	This file contains helper functions for the feed generator module.

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see LICENSE for more details.
'''



def ensure_format(val, allowed, required, allowed_values={}):
	if not val:
		return None
	# Make shure that we have a list of dicts. Even if there is only one.
	if not isinstance(val, list):
		val = [val]
	for elem in val:
		if not isinstance(elem, dict):
			raise ValueError('Invalid data (value is no dictionary)')
		if not set(elem.keys()) <= allowed:
			raise ValueError('Data contains invalid keys')
		if not set(elem.keys()) >= required:
			raise ValueError('Data contains not all required keys')
		for k,v in allowed_values.iteritems():
			if elem.get(k) and not elem[k] in v:
				raise ValueError('Invalid value for %s' % k )
	return val
