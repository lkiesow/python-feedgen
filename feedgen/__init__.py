# -*- coding: utf-8 -*-
"""
    =======
    feedgen
    =======

    This module can be used to generate web feeds in both ATOM and RSS format.
    It has support for extensions. Included is for example an extension to
    produce Podcasts.

    :copyright: 2013 by Lars Kiesow
    :license: FreeBSD and LGPL, see license.* for more details.


    -------------
    Create a Feed
    -------------

    To create a feed simply instantiate the FeedGenerator class and insert some
    data::

        >>> from feedgen.feed import FeedGenerator
        >>> fg = FeedGenerator()
        >>> fg.id('http://lernfunk.de/media/654321')
        >>> fg.title('Some Testfeed')
        >>> fg.author( {'name':'John Doe','email':'john@example.de'} )
        >>> fg.link( href='http://example.com', rel='alternate' )
        >>> fg.logo('http://ex.com/logo.jpg')
        >>> fg.subtitle('This is a cool feed!')
        >>> fg.link( href='http://larskiesow.de/test.atom', rel='self' )
        >>> fg.language('en')

    Note that for the methods which set fields that can occur more than once in
    a feed you can use all of the following ways to provide data:

    - Provide the data for that element as keyword arguments
    - Provide the data for that element as dictionary
    - Provide a list of dictionaries with the data for several elements

    Example::

        >>> fg.contributor(name='John Doe', email='jdoe@example.com' )
        >>> fg.contributor({'name':'John Doe', 'email':'jdoe@example.com'})
        >>> fg.contributor([{'name':'John', 'email':'jdoe@example.com'}, …])

    -----------------
    Generate the Feed
    -----------------

    After that you can generate both RSS or ATOM by calling the respective
    method::

        >>> atomfeed = fg.atom_str(pretty=True) # Get the ATOM feed as string
        >>> rssfeed  = fg.rss_str(pretty=True) # Get the RSS feed as string
        >>> fg.atom_file('atom.xml') # Write the ATOM feed to a file
        >>> fg.rss_file('rss.xml') # Write the RSS feed to a file


    ----------------
    Add Feed Entries
    ----------------

    To add entries (items) to a feed you need to create new FeedEntry objects
    and append them to the list of entries in the FeedGenerator. The most
    convenient way to do this, is to call the method add_entry(...) like this::

        >>> fe = fg.add_entry()
        >>> fe.id('http://lernfunk.de/media/654321/1')
        >>> fe.title('The First Episode')

    The FeedGenerator's method add_entry(...) will automatically create a new
    FeedEntry object, append it to the feeds internal list of entries and
    return it, so that additional data can be added.

    ----------
    Extensions
    ----------

    The FeedGenerator supports extension to include additional data into the
    XML structure of the feeds. Extensions can be loaded like this::

        >>> fg.load_extension('someext', atom=True, rss=True)

    This will try to load the extension “someext” from the file
    `ext/someext.py`. It is required that `someext.py` contains a class named
    “SomextExtension” which is required to have at least the two methods
    `extend_rss(...)` and `extend_atom(...)`. Although not required, it is
    strongly suggested to use BaseExtension from `ext/base.py` as superclass.

    `load_extension('someext', ...)` will also try to load a class named
    “SomextEntryExtension” for every entry of the feed. This class can be
    located either in the same file as SomextExtension or in
    `ext/someext_entry.py` which is suggested especially for large extensions.

    The parameters `atom` and `rss` tell the FeedGenerator if the extensions
    should only be used for either ATOM or RSS feeds. The default value for
    both parameters is true which means that the extension would be used for
    both kinds of feeds.

    **Example: Producing a Podcast**

    One extension already provided is the podcast extension. A podcast is an
    RSS feed with some additional elements for ITunes.

    To produce a podcast simply load the `podcast` extension::

        >>> from feedgen.feed import FeedGenerator
        >>> fg = FeedGenerator()
        >>> fg.load_extension('podcast')
        ...
        >>> fg.podcast.itunes_category('Technology', 'Podcasting')
        ...
        >>> fg.rss_str(pretty=True)
        >>> fg.rss_file('podcast.xml')

    Of cause the extension has to be loaded for the FeedEntry objects as well
    but this is done automatically by the FeedGenerator for every feed entry if
    the extension is loaded for the whole feed. You can, however, load an
    extension for a specific FeedEntry by calling `load_extension(...)` on that
    entry. But this is a rather uncommon use.

    Of cause you can still produce a normal ATOM or RSS feed, even if you have
    loaded some plugins by temporary disabling them during the feed generation.
    This can be done by calling the generating method with the keyword argument
    `extensions` set to `False`.

    ---------------------
    Testing the Generator
    ---------------------

    You can test the module by simply executing::

        $ python -m feedgen

"""
