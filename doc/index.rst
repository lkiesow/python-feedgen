======
PodGen
======

Wouldn't it be nice if there was a **clean and simple library** which could help you
**generate podcast RSS feeds** from your Python code? Well, today's your lucky day!

   >>> from podgen import Podcast, Episode, Media
   >>> # Create the Podcast
   >>> p = Podcast(
          name="My Awesome Podcast",
          description="My friends and I discuss Python"
                      " libraries each Tuesday!",
          website="http://example.org/awesomepodcast"
       )
   >>> # Add some episodes
   >>> p.episodes += [
          Episode(title="PodGen rocks!",
                  media=Media("http://example.org/ep1.mp3", 11932295),
                  summary="I found an awesome library for creating podcasts"),
          Episode(title="Heard about clint?",
                  media=Media("http://example.org/ep2.mp3", 15363464),
                  summary="The man behind Requests made something useful "
                          "for us command-line lovers."
       ]
   >>> # Generate the RSS feed
   >>> rss = str(p)

You don't need to read the RSS specification, write XML by hand or wrap your
head around ambiguous, undocumented APIs. Just provide the data, and PodGen
fixes the rest for you!

Where to start
--------------

Take a look at the :doc:`user/example` for a larger example, read about
:doc:`the project's background <user/introduction>` or refer to
the :doc:`user/basic_usage_guide/index` for a detailed introduction to PodGen.

Contents
--------

.. toctree::
   :maxdepth: 3

   user/index
   api
