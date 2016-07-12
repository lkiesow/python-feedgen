Creating the podcast
--------------------

Creating a new instance
~~~~~~~~~~~~~~~~~~~~~~~

::

    from podgen import Podcast
    p = Podcast()

Mandatory attributes
~~~~~~~~~~~~~~~~~~~~

::

    p.name = "My Example Podcast"
    p.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    p.website = "https://example.org"
    p.explicit = True

They're self explanatory, but you can read more about them if you'd like:

* :attr:`~podgen.Podcast.name`
* :attr:`~podgen.Podcast.description`
* :attr:`~podgen.Podcast.website`
* :attr:`~podgen.Podcast.explicit`

Image
~~~~~

A podcast's image is worth special attention::

    p.image = "https://example.com/static/example_podcast.png"

.. autoattribute:: podgen.Podcast.image
   :noindex:

Even though the image *technically* is optional, you won't reach people without it.

Optional attributes
~~~~~~~~~~~~~~~~~~~

There are plenty of other attributes that can be used with
:class:`podgen.Podcast <podgen.Podcast>`:


Commonly used
^^^^^^^^^^^^^

::

    p.copyright = "2016 Example Radio"
    p.language = "en-US"
    p.authors = [Person("John Doe", "editor@example.org")]
    p.feed_url = "https://example.com/feeds/podcast.rss"  # URL of this feed
    p.category = Category("Technology", "Podcasting")
    p.owner = p.authors[0]
    p.xslt = "https://example.com/feed/stylesheet.xsl"  # URL of XSLT stylesheet

Read more:

* :attr:`~podgen.Podcast.copyright`
* :attr:`~podgen.Podcast.language`
* :attr:`~podgen.Podcast.authors`
* :attr:`~podgen.Podcast.feed_url`
* :attr:`~podgen.Podcast.category`
* :attr:`~podgen.Podcast.owner`
* :attr:`~podgen.Podcast.xslt`


Less commonly used
^^^^^^^^^^^^^^^^^^

Some of those are obscure while some of them are often times not needed. Others
again have very reasonable defaults.

::

    # RSS Cloud enables podcatchers to subscribe to notifications when there's
    # a new episode ready, however it's not used much.
    p.cloud = ("server.example.com", 80, "/rpc", "cloud.notify", "xml-rpc")

    import datetime
    # pytz is a dependency of this library, and makes it easy to deal with
    # timezones. Generally, all dates must be timezone aware.
    import pytz
    # last_updated is datetime when the feed was last refreshed. If you don't
    # set it, the current date and time will be used instead when the feed is
    # generated, which is generally what you want. Nevertheless, you can
    # set your own date:
    p.last_updated = datetime.datetime(2016, 5, 18, 0, 0, tzinfo=pytz.utc))

    # publication_date is when the contents of this feed last were published.
    # If you don't set it, the date of the most recent Episode is used. Again,
    # this is generally what you want, but you can override it:
    p.publication_date = datetime.datetime(2016, 5, 17, 15, 32,tzinfo=pytz.utc))

    # Set of days on which podcatchers won't need to refresh the feed.
    # Not implemented widely.
    p.skip_days = {"Friday", "Saturday", "Sunday"}

    # Set of hours on which podcatchers won't need to refresh the feed.
    # Not implemented widely.
    p.skip_hours = set(range(8))
    p.skip_hours |= set(range(16, 24))

    # Person to contact regarding technical aspects of the feed.
    p.web_master = Person(None, "helpdesk@dallas.example.com")

    # Identify the software which generates the feed (defaults to python-podgen)
    p.set_generator("ExamplePodcastProgram", (1,0,0))
    # (you can also set the generator string directly)
    p.generator = "ExamplePodcastProgram v1.0.0 (with help from python-feedgen)"

    # !!! Be very careful about using the following attributes !!!

    # Tell iTunes that this feed has moved somewhere else.
    p.new_feed_url = "https://podcast.example.com/example"

    # Tell iTunes that this feed will never be updated again.
    p.complete = True

    # Tell iTunes that you'd rather not have this feed appear on iTunes.
    p.withhold_from_itunes = True

Read more:

* :attr:`~podgen.Podcast.cloud`
* :attr:`~podgen.Podcast.last_updated`
* :attr:`~podgen.Podcast.publication_date`
* :attr:`~podgen.Podcast.skip_days`
* :attr:`~podgen.Podcast.skip_hours`
* :attr:`~podgen.Podcast.web_master`
* :meth:`~podgen.Podcast.set_generator`
* :attr:`~podgen.Podcast.new_feed_url`
* :attr:`~podgen.Podcast.complete`
* :attr:`~podgen.Podcast.withhold_from_itunes`

Shortcut for filling in data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of creating a new :class:`.Podcast` object in one statement, and
populating it with data one statement at a time afterwards, you can create a
new :class:`.Podcast` object and fill it with data in one statement. Simply
use the attribute name as keyword arguments to the constructor::

   import podgen
   p = podgen.Podcast(
       <attribute name>=<attribute value>,
       <attribute name>=<attribute value>,
       ...
   )

Using this technique, you can define the Podcast as part of a list
comprehension, dictionaries and so on.
Take a look at the :doc:`API Documentation for Podcast </api.podcast>` for a
practical example.

--------------------------------------------------------------------------------

Next step is :doc:`part_2`.
