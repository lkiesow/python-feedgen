================
PodcastGenerator
================

.. warning::

   The documentation here represents how things *hopefully* will work once
   all the work is done. In the meantime, the :doc:`api` and the :doc:`user/example`
   should provide an accurate view of how to use this package.

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

You don't need to read the RSS specification, write XML by hand or wrap your
head around ambigous, undocumented APIs. Just provide the data, and PodcastGenerator
fixes the rest for you!

Where to start
--------------

Take a look at the :doc:`user/example` for a larger example, read about
:doc:`the project's background <user/introduction>` or refer to
the :doc:`user/use` for a detailed introduction to PodcastGenerator.

Contents
--------

.. toctree::
   :maxdepth: 3

   user/index
   api
