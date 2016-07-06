# -*- coding: utf-8 -*-
"""
    podgen.version
    ~~~~~~~~~~~~~~~

    :copyright: 2013-2015, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.

"""

'Version of python-podgen represented as tuple'
version = (0, 3, 2)


'Version of python-podgen represented as string'
version_str = '.'.join([str(x) for x in version])

version_major = version[:1]
version_minor = version[:2]
version_full  = version

version_major_str = '.'.join([str(x) for x in version_major])
version_minor_str = '.'.join([str(x) for x in version_minor])
version_full_str  = '.'.join([str(x) for x in version_full])

'Name of this project'
name = "python-podgen (podcastgen)"

'Website of this project'
website = "https://github.com/tobinus/python-podgen/tree/podcastgen"
