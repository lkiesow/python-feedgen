======
PodGen
======

.. image:: https://travis-ci.org/tobinus/python-podgen.svg?branch=master
    :target: https://travis-ci.org/tobinus/python-podgen

.. image:: https://readthedocs.org/projects/podgen/badge/?version=latest
   :target: http://podgen.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://badge.waffle.io/tobinus/python-podgen.svg?label=ready&title=Ready
   :target: https://waffle.io/tobinus/python-podgen
   :alt: 'Stories in Ready'

Don't you wish there was a **clean and simple library** which could help you
**generate podcast RSS feeds** with your Python code? Well, today's your lucky day!

   >>> from podgen import Podcast, Episode, Media
   >>> # Create the Podcast
   >>> p = Podcast(
          name="The Library Tuesday Talk",
          description="My friends and I discuss Python"
                      " libraries each Tuesday!",
          website="http://example.org/librarytuesdaytalk"
       )
   >>> # Add some episodes
   >>> p.episodes += [
          Episode(title="Worry about timezones no more",
                  media=Media("http://example.org/ep1.mp3", 11932295),
                  summary="Using pytz, you can make your code timezone-aware "
                          "with very little hassle."),
          Episode(title="Heard about clint?",
                  media=Media("http://example.org/ep2.mp3", 15363464),
                  summary="The man behind Requests made something useful "
                          "for us command-line nerds."
       ]
   >>> # Generate the RSS feed
   >>> rss = str(p)

You don't need to read the RSS specification, write XML by hand or wrap your
head around ambiguous, undocumented APIs. PodGen incorporates the industry's
best practices and lets you focus on collecting the necessary metadata and
publishing the podcast.


User Guide
----------

.. toctree::
   :maxdepth: 3

   user/introduction
   user/installation
   user/fork
   user/basic_usage_guide/part_1
   user/basic_usage_guide/part_2
   user/basic_usage_guide/part_3
   user/example
   advanced/index
   contributing
   api
