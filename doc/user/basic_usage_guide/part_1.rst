Populating the podcast
----------------------

Creating a new instance
~~~~~~~~~~~~~~~~~~~~~~~

::

    from feedgen import Podcast
    p = Podcast()

Mandatory properties
~~~~~~~~~~~~~~~~~~~~

::

    p.name = "My Example Podcast"
    p.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    p.website = "https://example.org"
    p.explicit = True

Those four properties, :attr:`~feedgen.feed.Podcast.name`,
:attr:`~feedgen.feed.Podcast.description`,
:attr:`~feedgen.feed.Podcast.explicit` and
:attr:`~feedgen.feed.Podcast.website`, are actually
the only four **mandatory** properties of
:class:`~feedgen.feed.Podcast`. A summary of them:

.. autosummary::

   ~feedgen.feed.Podcast.name
   ~feedgen.feed.Podcast.description
   ~feedgen.feed.Podcast.website
   ~feedgen.feed.Podcast.explicit

Image
~~~~~

A podcast's image is worth special attention::

    p.image = "https://example.com/static/example_podcast.png"

.. automethod:: feedgen.feed.Podcast.itunes_image
   :noindex:

Even though the image *technically* is optional, you won't reach people without it.

Optional properties
~~~~~~~~~~~~~~~~~~~

There are plenty of other properties that can be used with
:class:`feedgen.feed.Podcast <feedgen.Podcast>`:


Commonly used
^^^^^^^^^^^^^

::

    p.copyright = "2016 Example Radio"
    p.language = "en-US"
    p.authors = [Person("John Doe", "editor@example.org")]
    p.feed_url = "https://example.com/feeds/podcast.rss"
    p.category = Category("Technology", "Podcasting")
    p.owner = p.authors[0]

.. autosummary::

   ~feedgen.feed.Podcast.copyright
   ~feedgen.feed.Podcast.language
   ~feedgen.feed.Podcast.authors
   ~feedgen.feed.Podcast.feed_url
   ~feedgen.feed.Podcast.category
   ~feedgen.feed.Podcast.owner


Less commonly used
^^^^^^^^^^^^^^^^^^

Some of those are obscure while some of them are often times not needed. Others
again have very reasonable defaults. Remember to click on a name to read its
full description.

::

    p.cloud = ("server.example.com", "/rpc", 80, "xml-rpc")

    import datetime
    import pytz
    p.updated = datetime.datetime(2016, 5, 18, 0, 0, tzinfo=pytz.utc))
    p.published = datetime.datetime(2016, 5, 17, 15, 32, tzinfo=pytz.utc))

    p.skipDays = {"Friday", "Saturday", "Sunday"}
    p.skipHours = set(range(8))
    p.skipHours |= set(range(16, 24))
    p.webMaster = Person(None, "helpdesk@dallas.example.com")
    # Be very careful about using the following attributes:
    p.new_feed_url = "https://podcast.example.com/example"
    p.complete = True
    p.withhold_from_itunes = True

.. autosummary::

   ~feedgen.feed.Podcast.cloud
   ~feedgen.feed.Podcast.updated
   ~feedgen.feed.Podcast.published
   ~feedgen.feed.Podcast.skipDays
   ~feedgen.feed.Podcast.skipHours
   ~feedgen.feed.Podcast.webMaster
   ~feedgen.feed.Podcast.new_feed_url
   ~feedgen.feed.Podcast.complete
   ~feedgen.feed.Podcast.withhold_from_itunes


Next step is :doc:`part_2`.
