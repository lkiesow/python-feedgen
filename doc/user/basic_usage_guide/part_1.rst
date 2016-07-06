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

Those four properties, :attr:`~feedgen.Podcast.name`,
:attr:`~feedgen.Podcast.description`,
:attr:`~feedgen.Podcast.explicit` and
:attr:`~feedgen.Podcast.website`, are actually
the only four **mandatory** properties of
:class:`~feedgen.Podcast`.

Image
~~~~~

A podcast's image is worth special attention::

    p.image = "https://example.com/static/example_podcast.png"

.. autoattribute:: feedgen.Podcast.image
   :noindex:

Even though the image *technically* is optional, you won't reach people without it.

Optional properties
~~~~~~~~~~~~~~~~~~~

There are plenty of other properties that can be used with
:class:`feedgen.Podcast <feedgen.Podcast>`:


Commonly used
^^^^^^^^^^^^^

::

    p.copyright = "2016 Example Radio"
    p.language = "en-US"
    p.authors = [Person("John Doe", "editor@example.org")]
    p.feed_url = "https://example.com/feeds/podcast.rss"
    p.category = Category("Technology", "Podcasting")
    p.owner = p.authors[0]

Read more:

* :attr:`~feedgen.Podcast.copyright`
* :attr:`~feedgen.Podcast.language`
* :attr:`~feedgen.Podcast.authors`
* :attr:`~feedgen.Podcast.feed_url`
* :attr:`~feedgen.Podcast.category`
* :attr:`~feedgen.Podcast.owner`


Less commonly used
^^^^^^^^^^^^^^^^^^

Some of those are obscure while some of them are often times not needed. Others
again have very reasonable defaults.

::

    p.cloud = ("server.example.com", 80, "/rpc", "cloud.notify", "xml-rpc")

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

Read more:

* :attr:`~feedgen.Podcast.cloud`
* :attr:`~feedgen.Podcast.last_updated`
* :attr:`~feedgen.Podcast.publication_date`
* :attr:`~feedgen.Podcast.skip_days`
* :attr:`~feedgen.Podcast.skip_hours`
* :attr:`~feedgen.Podcast.web_master`
* :attr:`~feedgen.Podcast.new_feed_url`
* :attr:`~feedgen.Podcast.complete`
* :attr:`~feedgen.Podcast.withhold_from_itunes`

Shortcut for filling in data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of creating a new :class:`.Podcast` object in one statement, and
populating it with data one statement at a time afterwards, you can create a
new :class:`.Podcast` object and fill it with data in one statement. Simply
use the attribute name as keyword arguments to the constructor::

   import feedgen
   p = feedgen.Podcast(
       <attribute name>=<attribute value>,
       <attribute name>=<attribute value>,
       ...
   )

Take a look at the :doc:`API Documentation for Podcast </api.podcast>` for a
practical example.

--------------------------------------------------------------------------------

Next step is :doc:`part_2`.
