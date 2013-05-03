=============
feedgenerator
=============

This module can be used to generate web feeds in both ATOM and RSS format.
The included PodcastGenerator furthermore includes all of Apples RSS
extension for Podcasts.

- copyright: 2013 by Lars Kiesow
- license: FreeBSD and LGPL, see license.bsd or license.lgpl for more details.


-------------
Create a Feed
-------------

To create a feed simply instanciate the FeedGenerator class and insert some
data::

	>>> from feedgenerator.feed import FeedGenerator
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

- Provide the data for that element as keyword arguments::
- Provide the data for that element as dictionary::
- Provide a list of dictionaries with the data for several elements::

Example::

	>>> fg.contributor( name='John Doe', email='jdoe@example.com' )
	>>> fg.contributor({'name':'John Doe', 'email':'jdoe@example.com'})
	>>> fg.contributor([{'name':'John Doe', 'email':'jdoe@example.com'}, ...])

---------------
Generate output
---------------

After that you can generate both RSS or ATOM by calling the respective method::

	>>> atomfeed = fg.atom_str(pretty=True) # Get the ATOM feed as string
	>>> rssfeed  = fg.rss_str(pretty=True) # Get the RSS feed as string
	>>> fg.atom_file('atom.xml') # Write the ATOM feed to a file
	>>> fg.rss_file('rss.xml') # Write the RSS feed to a file


----------------
Add Feed Entries
----------------

To add entries (items) to a feed you need to create new FeedEntry objects
and append them to the list of entries in the FeedGenerator. The most
convenient way to go is to use the FeedGenerator itself for the
instantiation of the FeedEntry object::

	>>> fe = fg.add_entry()
	>>> fe.id('http://lernfunk.de/media/654321/1')
	>>> fe.title('The First Episode')

The FeedGenerators method add_entry(...) without argument provides will
automaticall generate a new FeedEntry object, append it to the feeds
internal list of entries and return it, so that additional data can be
added.

-----------------
Produce a Podcast
-----------------

A podcast is an RSS feed with some additional elements for ITunes. The
feedgenerator has a PodcastGenerator class as extension to the default
FeedGenerator which you can use to set these additional fields.

To produce a podcast simply do something like this::

	>>> from feedgenerator.podcast import PodcastGenerator
	>>> fg = PodcastGenerator()
	...
	>>> fg.podcast_str(pretty=True)
	>>> fg.podcast_file('podcast.xml')

For the episodes of the podcast you should also use PodcastEntry instead of
FeedEntry. However, if you use the add_entry(...) method to generator the
entry objects, it will take care of that for you.

Of cause you can still produce a normat ATOM or RSS feed, even if you use
the PodcastGenerator using the {atom,rss}_{str,file} methods.

---------------------
Testing the Generator
---------------------

You can test the module by simply executing::

	%> pythom -m feedgenerator 

If you want to have a look at the code for this test to have a working code
example for a whole feed generation process, you can find it in the
[__main__.py](https://github.com/lkiesow/pyFeedGenerator/blob/master/feedgenerator/__main__.py#L36).
