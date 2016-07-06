===================================
PodGen (forked from python-feedgen)
===================================

[![Build Status](https://travis-ci.org/tobinus/python-podgen.svg?branch=master)](https://travis-ci.org/tobinus/python-podgen)

This module can be used to generate podcast feeds in RSS format.

It is licensed under the terms of both, the FreeBSD license and the LGPLv3+.
Choose the one which is more convenient for you. For more details have a look
at license.bsd and license.lgpl.

More details about the project:

- Repository:            https://github.com/tobinus/python-podgen
- Documentation:         http://lkiesow.github.io/python-feedgen/
- Python Package Index:  https://pypi.python.org/pypi/podgen/


------------
Installation
------------

Currently, you'll need to clone this repository, and create a virtualenv and
install lxml and dateutils.


----------
Known bugs
----------

* We do not follow the RSS recommendation to encode &amp;, &lt; and &gt; using
  hexadecimal character reference (eg. `&#x3C;`), simply because lxml provides
  no documentation on how to do that when using the text property.
