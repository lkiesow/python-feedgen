Populating the podcast
----------------------

Creating a new instance
~~~~~~~~~~~~~~~~~~~~~~~

::

    from podgen import Podcast
    p = Podcast()

Mandatory properties
~~~~~~~~~~~~~~~~~~~~

::

    p.name = "My Example Podcast"
    p.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    p.website = "https://example.org"
    p.explicit = True

Those four properties, :attr:`~podgen.Podcast.name`,
:attr:`~podgen.Podcast.description`,
:attr:`~podgen.Podcast.explicit` and
:attr:`~podgen.Podcast.website`, are actually
the only four **mandatory** properties of
:class:`~podgen.Podcast`.

Image
~~~~~

A podcast's image is worth special attention::

    p.image = "https://example.com/static/example_podcast.png"

.. autoattribute:: podgen.Podcast.image
   :noindex:

Even though the image *technically* is optional, you won't reach people without it.

Optional properties
~~~~~~~~~~~~~~~~~~~

There are plenty of other properties that can be used with
:class:`podgen.Podcast <podgen.Podcast>`:


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

* :attr:`~podgen.Podcast.copyright`
* :attr:`~podgen.Podcast.language`
* :attr:`~podgen.Podcast.authors`
* :attr:`~podgen.Podcast.feed_url`
* :attr:`~podgen.Podcast.category`
* :attr:`~podgen.Podcast.owner`


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

* :attr:`~podgen.Podcast.cloud`
* :attr:`~podgen.Podcast.last_updated`
* :attr:`~podgen.Podcast.publication_date`
* :attr:`~podgen.Podcast.skip_days`
* :attr:`~podgen.Podcast.skip_hours`
* :attr:`~podgen.Podcast.web_master`
* :attr:`~podgen.Podcast.new_feed_url`
* :attr:`~podgen.Podcast.complete`
* :attr:`~podgen.Podcast.withhold_from_itunes`

Shortcut for filling in data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Take a look at the :doc:`API Documentation for Podcast </api.podcast>` for a
practical example.

--------------------------------------------------------------------------------

Next step is :doc:`part_2`.
