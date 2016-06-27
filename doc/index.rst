================
PodcastGenerator
================

Wouldn't it be nice if there was a clean, simple library which could help you
generate podcast RSS feeds from your Python code? Well, today's your lucky day!

   >>> from feedgen import Podcast
   >>> # Create the Podcast
   >>> p = Podcast(
          name="My Awesome Podcast",
          description="My friends and I discuss Python"
                      " libraries each Tuesday!",
          website="http://example.org/awesomepodcast"
       )
   >>> # Add some episodes
   >>> p.episodes += [
          p.Episode(title="PodcastGenerator rocks!",
                    media=p.Media("http://example.org/ep1.mp3", 11932295),
                    summary="I found an awesome library for creating podcasts"),
          p.Episode(title="Heard about clint?",
                    media=p.Media("http://example.org/ep2.mp3", 15363464),
                    summary="The man behind Requests made something useful "
                            "for us command-line lovers."
       ]
   >>> # Generate the RSS feed
   >>> rss = str(p)

You don't need to read the RSS specification, you don't need to think about
how iTunes interprets things. Just fill in the data, and PodcastGenerator
does the rest for you.



-----------------
Generate the Feed
-----------------

After that you can generate RSS by calling::

    >>> rssfeed  = fg.rss_str() # Get the RSS feed as string
    >>> fg.rss_file('rss.xml', minimize=True) # Write the RSS feed to a file


----------------
Add Feed Entries
----------------

To add entries (items) to a feed you need to create new BaseEpisode objects and
append them to the list of entries in the Podcast. The most convenient
way to go is to use the Podcast itself for the instantiation of the
BaseEpisode object::

    >>> fe = fg.add_episode()
    >>> fe.id('http://lernfunk.de/media/654321/1')
    >>> fe.title('The First Episode')

The Podcast method `add_episode(...)` without argument provides will
automatically generate a new BaseEpisode object, append it to the feeds internal
list of entries and return it, so that additional data can be added.

--------------------------
Using the podcast features
--------------------------

All iTunes-specific features are available as methods that start with `itunes_`,
although most features are platform agnostic::

    >>> from feedgen.feed import Podcast
    >>> fg = Podcast()
    ...
    >>> fg.itunes_category('Technology', 'Podcasting')
    ...
    >>> fe = fg.add_episode()
    >>> fe.id('http://lernfunk.de/media/654321/1/file.mp3')
    >>> fe.title('The First Episode')
    >>> fe.description('Enjoy our first episode.')
    >>> fe.enclosure('http://lernfunk.de/media/654321/1/file.mp3', 0, 'audio/mpeg')
    ...
    >>> fg.rss_str()
    >>> fg.rss_file('podcast.xml', minimize=True)



---------------------
Testing the Generator
---------------------

You can test the module integration-testing-style by simply executing::

    $ python -m feedgen

If you want to have a look at the code for this test to have a working code
example for a whole feed generation process, you can find it in the
[`__main__.py`](https://github.com/tobinus/python-feedgen/blob/podcastgen/feedgen/__main__.py).

.. toctree::
   :hidden:

   user/index
   api
