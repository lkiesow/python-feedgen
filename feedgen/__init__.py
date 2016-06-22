# -*- coding: utf-8 -*-
"""
    =============
    Feedgenerator (forked)
    =============

    Ignore:
    [![Build Status](https://travis-ci.org/lkiesow/python-feedgen.svg?branch=master)
    ](https://travis-ci.org/lkiesow/python-feedgen)

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

    To create a feed simply instantiate the FeedGenerator class and insert some
    data::

        >>> from feedgen.feed import FeedGenerator
        >>> fg = FeedGenerator()
        >>> fg.title('Some Testfeed')
        >>> fg.author( {'name':'John Doe','email':'john@example.de'} )
        >>> fg.link( href='http://example.com', rel='alternate' )
        >>> fg.image('http://ex.com/logo.jpg')
        >>> fg.description('This is a cool feed!')
        >>> fg.link( href='http://larskiesow.de/test.atom')
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

    -----------------
    Generate the Feed
    -----------------

    After that you can generate RSS by calling::

        >>> rssfeed  = fg.rss_str(pretty=True) # Get the RSS feed as string
        >>> fg.rss_file('rss.xml') # Write the RSS feed to a file


    ----------------
    Add Feed Entries
    ----------------

    To add entries (items) to a feed you need to create new FeedEntry objects and
    append them to the list of entries in the FeedGenerator. The most convenient
    way to go is to use the FeedGenerator itself for the instantiation of the
    FeedEntry object::

        >>> fe = fg.add_entry()
        >>> fe.guid('http://lernfunk.de/media/654321/1')
        >>> fe.title('The First Episode')

    The FeedGenerators method `add_entry(...)` without argument provides will
    automatically generate a new FeedEntry object, append it to the feeds internal
    list of entries and return it, so that additional data can be added.

    --------------------------
    Using the podcast features
    --------------------------

    All iTunes-specific features are available as methods that start with `itunes_`,
    although most features are platform agnostic::

        >>> from feedgen.feed import FeedGenerator
        >>> fg = FeedGenerator()
        ...
        >>> fg.itunes_category('Technology', 'Podcasting')
        ...
        >>> fe = fg.add_entry()
        >>> fe.guid('http://lernfunk.de/media/654321/1/file.mp3')
        >>> fe.title('The First Episode')
        >>> fe.description('Enjoy our first episode.')
        >>> fe.enclosure('http://lernfunk.de/media/654321/1/file.mp3', 0, 'audio/mpeg')
        ...
        >>> fg.rss_str(pretty=True)
        >>> fg.rss_file('podcast.xml')



    ---------------------
    Testing the Generator
    ---------------------

    You can test the module integration-testing-style by simply executing::

        $ python -m feedgen

    If you want to have a look at the code for this test to have a working code
    example for a whole feed generation process, you can find it in the
    [`__main__.py`](https://github.com/tobinus/python-feedgen/blob/podcastgen/feedgen/__main__.py).


"""
