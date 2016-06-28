==============================================
Feedgenerator (forked) - Podcasting for humans
==============================================

Ignore:
[![Build Status](https://travis-ci.org/lkiesow/python-feedgen.svg?branch=master)
](https://travis-ci.org/lkiesow/python-feedgen)

**Note: This document is in the process of being rewritten.**

This module can be used to generate podcast feeds in RSS format.

It is licensed under the terms of both, the FreeBSD license and the LGPLv3+.
Choose the one which is more convenient for you. For more details have a look
at license.bsd and license.lgpl.

More details about the project:

- Repository:            https://github.com/lkiesow/python-feedgen
- Documentation:         http://lkiesow.github.io/python-feedgen/
- Python Package Index:  https://pypi.python.org/pypi/feedgen/


------------
Installation
------------

Currently, you'll need to clone this repository, and create a virtualenv and
install lxml and dateutils.


-------------
Create a Feed
-------------

To create a feed simply instantiate the Podcast class and insert some
data::

    >>> from feedgen.feed import Podcast
    >>> fg = Podcast()
    >>> fg.name('Some Testfeed')
    >>> fg.author( {'name':'John Doe','email':'john@example.de'} )
    >>> fg.website( href='http://example.com', rel='alternate' )
    >>> fg.image('http://ex.com/logo.jpg')
    >>> fg.description('This is a cool feed!')
    >>> fg.website( href='http://larskiesow.de/test.atom')
    >>> fg.language('en')

Note that for the methods which set fields that can occur more than once in a
feed you can use all of the following ways to provide data:

- Provide the data for that element as keyword arguments
- Provide the data for that element as dictionary
- Provide a list of dictionaries with the data for several elements

Example::

    >>> fg.contributor( name='John Doe', email='jdoe@example.com' )
    >>> fg.contributor({'name':'John Doe', 'email':'jdoe@example.com'})
    >>> fg.contributor([{'name':'John Doe', 'email':'jdoe@example.com'}, ...])

----------
Known bugs
----------

* We do not follow the RSS recommendation to encode &amp;, &lt; and &gt; using
  hexadecimal character reference (eg. `&#x3C;`), simply because lxml provides
  no documentation on how to do that when using the text property.
