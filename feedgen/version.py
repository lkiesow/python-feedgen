# -*- coding: utf-8 -*-
'''
	feedgen.version
	~~~~~~~~~~~~~~~

	:copyright: 2013, Lars Kiesow <lkiesow@uos.de>

	:license: FreeBSD and LGPL, see license.* for more details.

'''

'Version of python-feedgen represented as tuple'
version_elements = (0, 2, 3)


'Version of python-feedgen represented as string'
version = '.'.join([str(x) for x in version_elements])
