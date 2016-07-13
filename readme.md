===================================
PodGen (forked from python-feedgen)
===================================

[![Build Status](https://travis-ci.org/tobinus/python-podgen.svg?branch=master)](https://travis-ci.org/tobinus/python-podgen)
[![Documentation Status](https://readthedocs.org/projects/podgen/badge/?version=latest)](http://podgen.readthedocs.io/en/latest/?badge=latest)
[![Stories in Ready](https://badge.waffle.io/tobinus/python-podgen.svg?label=ready&title=Ready)](http://waffle.io/tobinus/python-podgen)


This module can be used to generate podcast feeds in RSS format, and is
compatible with Python 2.7 and 3.3+.

It is licensed under the terms of both, the FreeBSD license and the LGPLv3+.
Choose the one which is more convenient for you. For more details have a look
at license.bsd and license.lgpl.

More details about the project:

- Repository:            https://github.com/tobinus/python-podgen
- Documentation:         https://podgen.readthedocs.io/
- Python Package Index:  https://pypi.python.org/pypi/podgen/


See the documentation link above for installation instructions and
guides on how to use this module.

----------
Known bugs
----------

* We do not follow the RSS recommendation to encode &amp;, &lt; and &gt; using
  hexadecimal character reference (eg. `&#x3C;`), simply because lxml provides
  no documentation on how to do that when using the text property.
