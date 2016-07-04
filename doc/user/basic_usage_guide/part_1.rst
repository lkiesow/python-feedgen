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

Those four properties, :attr:`~feedgen.podcast.Podcast.name`,
:attr:`~feedgen.podcast.Podcast.description`,
:attr:`~feedgen.podcast.Podcast.explicit` and
:attr:`~feedgen.podcast.Podcast.website`, are actually
the only four **mandatory** properties of
:class:`~feedgen.podcast.Podcast`. A summary of them:

.. autosummary::

   ~feedgen.podcast.Podcast.name
   ~feedgen.podcast.Podcast.description
   ~feedgen.podcast.Podcast.website
   ~feedgen.podcast.Podcast.explicit

Image
~~~~~

A podcast's image is worth special attention::

    p.image = "https://example.com/static/example_podcast.png"

.. automethod:: feedgen.podcast.Podcast.image
   :noindex:

Even though the image *technically* is optional, you won't reach people without it.

Optional properties
~~~~~~~~~~~~~~~~~~~

There are plenty of other properties that can be used with
:class:`feedgen.podcast.Podcast <feedgen.Podcast>`:


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

   ~feedgen.podcast.Podcast.copyright
   ~feedgen.podcast.Podcast.language
   ~feedgen.podcast.Podcast.authors
   ~feedgen.podcast.Podcast.feed_url
   ~feedgen.podcast.Podcast.category
   ~feedgen.podcast.Podcast.owner


Less commonly used
^^^^^^^^^^^^^^^^^^

Some of those are obscure while some of them are often times not needed. Others
again have very reasonable defaults. Remember to click on a name to read its
full description.

::

    p.cloud = ("server.example.com", "/rpc", 80, "xml-rpc")

    import datetime
    import pytz
    p.last_updated = datetime.datetime(2016, 5, 18, 0, 0, tzinfo=pytz.utc))
    p.publication_date = datetime.datetime(2016, 5, 17, 15, 32, tzinfo=pytz.utc))

    p.skip_days = {"Friday", "Saturday", "Sunday"}
    p.skip_hours = set(range(8))
    p.skip_hours |= set(range(16, 24))
    p.web_master = Person(None, "helpdesk@dallas.example.com")
    # Be very careful about using the following attributes:
    p.new_feed_url = "https://podcast.example.com/example"
    p.complete = True
    p.withhold_from_itunes = True

.. autosummary::

   ~feedgen.podcast.Podcast.cloud
   ~feedgen.podcast.Podcast.last_updated
   ~feedgen.podcast.Podcast.publication_date
   ~feedgen.podcast.Podcast.skip_days
   ~feedgen.podcast.Podcast.skip_hours
   ~feedgen.podcast.Podcast.web_master
   ~feedgen.podcast.Podcast.new_feed_url
   ~feedgen.podcast.Podcast.complete
   ~feedgen.podcast.Podcast.withhold_from_itunes


Next step is :doc:`part_2`.
