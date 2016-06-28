Basic usage guide
=================

When using PodcastGenerator, you can divide your program into
three phases:

#. Populating the podcast
#. Adding episodes
#. Generating the RSS

While the
:doc:`example` gives you a practical introduction, this document helps you
understand what the different attributes mean and how they should be used.
It complements the :doc:`../api` nicely.

Populating the podcast
----------------------

Creating a new instance
~~~~~~~~~~~~~~~~~~~~~~~

::

    from feedgen import Podcast
    p = Podcast()

Mandatory properties
~~~~~~~~~~~~~~~~~~~~

Next, we will give the podcast some metadata::

    p.name = "My Example Podcast"
    p.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    p.website = "https://example.org"

Those three properties, :attr:`~feedgen.feed.Podcast.name`,
:attr:`~feedgen.feed.Podcast.description` and
:attr:`~feedgen.feed.Podcast.website`, are actually
the only three **mandatory** properties of
:class:`~feedgen.feed.Podcast`. A summary of them:

.. autosummary::

   ~feedgen.feed.Podcast.name
   ~feedgen.feed.Podcast.description
   ~feedgen.feed.Podcast.website

Image
~~~~~

A podcast's image is worth special attention::

    p.image = "https://example.com/static/example_podcast.png"

.. automethod:: feedgen.feed.Podcast.itunes_image
   :noindex:

Even though the image *technically* is optional, you won't reach people without.

Optional properties
~~~~~~~~~~~~~~~~~~~

There are plenty of other properties that can be used with
:class:`feedgen.feed.Podcast <feedgen.Podcast>`:


Commonly used
^^^^^^^^^^^^^

::

    p.copyright = "© 2016 Example Radio"
    p.language = "en-US"
    p.managingEditor = p.Person("John Doe", "editor@example.org")
    p.feed_url = "https://example.com/feeds/podcast.rss"
    p.category = Category("Technology", "Podcasting")
    p.explicit = True
    p.owner = p.managingEditor

.. autosummary::

   ~feedgen.feed.Podcast.copyright
   ~feedgen.feed.Podcast.language
   ~feedgen.feed.Podcast.managingEditor
   ~feedgen.feed.Podcast.feed_url
   ~feedgen.feed.Podcast.category
   ~feedgen.feed.Podcast.explicit
   ~feedgen.feed.Podcast.owner


Less commonly used
^^^^^^^^^^^^^^^^^^

Some of those are obscure while some of them are often times not needed. Others
again have very reasonable defaults. Remember to click on a name to read its
full description.

::

    p.cloud = p.CloudService("server.example.com", "/rpc", 80, "xml-rpc")

    import datetime
    import pytz
    p.updated = datetime.datetime(2016, 5, 18, 0, 0, tzinfo=pytz.utc))
    p.published = datetime.datetime(2016, 5, 17, 15, 32, tzinfo=pytz.utc))

    p.skipDays = {"Friday", "Saturday", "Sunday"}
    p.skipHours = set(range(8))
    p.skipHours |= set(range(16, 24))
    p.webMaster = p.Person(None, "helpdesk@dallas.example.com")
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



Adding episodes
---------------

To add episodes to a feed, you need to create new
:attr:`feedgen.Podcast` objects and
append them to the list of entries in the Podcast. That is pretty
straight-forward::

    my_episode = p.Episode()
    p.episodes.append(my_episode)

There is a conveinence method called :meth:`Podcast.add_episode <feedgen.feed.Podcast.add_episode>`
which optionally creates a new instance of ``Episode``, adds it to the podcast
and returns it, allowing you to assign it to a variable::

    my_episode = p.add_episode()

If you prefer to use the constructor, there's nothing wrong with that::

    my_episode = p.add_episode(p.Episode())

The advantage of using the latter form, is that you can pass data to the
constructor, which can make your code more compact and readable.

Filling with data
~~~~~~~~~~~~~~~~~

There is only one rule for episodes: **they must have either a title or a
summary**, or both. Additionally, you can opt to have a long summary, as
well as a short subtitle::

    my_episode.title = "S01E10: The Best Example of them All"
    my_episode.subtitle = "We found the greatest example!"
    my_episode.summary = "In this week's episode, we have found the " + \
                         "<i>greatest</i> example of them all."
    my_episode.long_summary = "In this week's episode, we went out on a " + \
        "search to find the <i>greatest</i> example of them " + \
        "all. <br/>Today's intro music: " + \
        "<a href='https://www.youtube.com/watch?v=dQw4w9WgXcQ'>Example Song</a>"

They're all pretty obvious:

.. autosummary::

   ~feedgen.item.BaseEpisode.title
   ~feedgen.item.BaseEpisode.subtitle
   ~feedgen.item.BaseEpisode.summary
   ~feedgen.item.BaseEpisode.long_summary

Enclosing media
^^^^^^^^^^^^^^^

Of course, this isn't much of a podcast if we don't have any **media**
attached to it! ::

    my_episode.media = p.Media("http://example.com/podcast/s01e10.mp3",
                               size=p.Media.Auto,
                               duration="1:02:36")

Normally, you must specify how big the **file size** is in bytes, but PodcastGenerator
can send a HEAD request to the URL and retrieve how many bytes it is
automatically by using p.Media.Auto as shown. This only works if `requests <http://docs.python-requests.org/en/master/>`_
is installed, though! If you know how big it is, you're better off not using
this feature, like this::

    my_episode.media = p.Media("http://example.com/podcast/s01e10.mp3",
                               size=17475653,
                               duration="1:02:36")

The **type** of the media file is derived from the URI ending. Even though you
technically can have file names which don't end in their actual file extension,
iTunes will use the file extension to determine what type of file it is, without
even asking the server. You must therefore make sure your media files have the
correct file extension.

The **duration** is also important to include, for your listeners' convenience.
Without it, they won't know how long an episode is before they start downloading
and listening.

.. autosummary::

   ~feedgen.item.BaseEpisode.media
   ~feedgen.feed.Podcast.Media


Identifying the episode
^^^^^^^^^^^^^^^^^^^^^^^

Every episode is identified by a **globally unique identifier (GUID)**.
By default, this id is set to be the same as the URL of the media (see above)
when the feed is generated.
That is, given the example above, the id of ``my_episode`` would be
``http://example.com/podcast/s01e10.mp3``.

This has the implication that **if you don't set id, the media URL must stay
the same**.

.. autosummary:: ~feedgen.item.BaseEpisode.id


Episode's publication date
^^^^^^^^^^^^^^^^^^^^^^^^^^

An episode's publication date indicates when the episode first went live. It is
used to indicate how old the episode is, and a client may say an episode is from
"1 hour ago", "yesterday", "last week" and so on. You should therefore make sure
that it matches the exact time that the episode went live, or else your listeners
will get a new episode which appears to have existed for longer than it has.
This is why it's generally a bad idea to use the media file's modification date
as the publication date when you make your episodes some time in advance
– your listeners will suddenly get an "old" episode in
their feed! ::

   my_episode.published_date = datetime.datetime(2016, 5, 18, 10, 0,
                                                 tzinfo=pytz.utc)

.. autosummary:: ~feedgen.item.BaseEpisode.published_date


The Link
^^^^^^^^

If you're publishing articles along with your podcast episodes, you should
link to the relevant article. Examples can be linking to the sound on
SoundCloud or the post on your website. Usually, your
listeners expect to find the entirety of the :attr:`~feedgen.item.BaseEpisode.summary` by following
the link. ::

    my_episode.link = "http://example.com/article/2016/05/18/Best-example"

If you don't have anything to link to, then that's fine as well. No link is
better than a disappointing link.

.. autosummary:: ~feedgen.item.BaseEpisode.link


The Author
^^^^^^^^^^

There is no point in copy+pasting the same author name in every single episode.
Instead, you should just set :attr:`Podcast.managingEditor <feedgen.feed.Podcast.managingEditor>`
to the appropriate name and/or email address, and don't set any authors on the
episodes. iTunes and others are smart enough to understand that the person
or entity named in :attr:`Podcast.managingEditor <feedgen.feed.Podcast.managingEditor>`
is responsible for all episodes.

If the author of an episode differs from the rest, though, you can use
:attr:`the author attribute <feedgen.item.BaseEpisode.author>` to indicate that::

     my_episode.author = Person("Joe Bob")

You can even have multiple authors::

     my_episode.author = [Person("Joe Bob"), Person("Alice Bob")]

.. autosummary:: ~feedgen.item.BaseEpisode.author


Category
^^^^^^^^

An episode can have a different category than the rest of the podcast::

     my_episode.category = Category("Arts", "Food")

.. autosummary:: ~feedgen.item.BaseEpisode.category


Less used attributes
^^^^^^^^^^^^^^^^^^^^

::

    my_episode.image = "http://example.com/static/best-example.png"
    my_episode.explicit = False
    my_episode.is_close_captioned = False  # Only applicable for video
    my_episode.order = 1
    # Be careful about using the following attribute!
    my_episode.withhold_from_itunes = True

.. autosummary::

   ~feedgen.item.BaseEpisode.image
   ~feedgen.item.BaseEpisode.explicit
   ~feedgen.item.BaseEpisode.is_close_captioned
   ~feedgen.item.BaseEpisode.order
   ~feedgen.item.BaseEpisode.withhold_from_itunes

Generating the RSS
------------------

Once you've added all the information and all episodes, it's time to
take the final step::

    rssfeed  = p.rss_str()
    # Print to stdout, just as an example
    print(rssfeed)

If you're okay with the default parameters of :meth:`feedgen.feed.Podcast.rss_str`,
you can use a shortcut by converting :class:`~feedgen.feed.Podcast` to :obj:`str`::

    rssfeed = str(p)
    # Or let print convert to str for you
    print(p)

Doing so is the same as calling :meth:`feedgen.feed.Podcast.rss_str` with no
parameters.

.. autosummary::

    ~feedgen.feed.Podcast.rss_str

You may also write the feed to a file directly, using :meth:`feedgen.feed.Podcast.rss_file`::

    fg.rss_file('rss.xml', minimize=True)


.. autosummary::

    ~feedgen.feed.Podcast.rss_file


