
Adding episodes
---------------

To add episodes to a feed, you need to create new
:attr:`Podcast.Episode <feedgen.feed.Podcast.Episode>` objects and
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

.. warning::

   An episode's ID should never change. Therefore, **if you don't set id, the
   media URL must never change either**.

.. autosummary:: ~feedgen.item.BaseEpisode.id


Episode's publication date
^^^^^^^^^^^^^^^^^^^^^^^^^^

An episode's publication date indicates when the episode first went live. It is
used to indicate how old the episode is, and a client may say an episode is from
"1 hour ago", "yesterday", "last week" and so on. You should therefore make sure
that it matches the exact time that the episode went live, or else your listeners
will get a new episode which appears to have existed for longer than it has.

.. note::

   It is generally a bad idea to use the media file's modification date
   as the publication date when you make your episodes some time in advance
   – your listeners will suddenly get an "old" episode in
   their feed!

::

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

.. note::

   If you don't have anything to link to, then that's fine as well. No link is
   better than a disappointing link.

.. autosummary:: ~feedgen.item.BaseEpisode.link


The Author
^^^^^^^^^^

.. note::

   Some of those attributes correspond to attributes found in
   :class:`~feedgen.feed.Podcast`. In such cases, you should only set those
   attributes at the episode level if they **differ** from their value at the
   podcast level.

Normally, the attributes :attr:`Podcast.author <feedgen.feed.Podcast.author>`
and :attr:`Podcast.webMaster <feedgen.feed.Podcast.webMaster>` (if set) are
used to determine the author of an episode. Thus, if all your episodes have
the same author, you should just set it at the podcast level.

If an episode's author differs from the podcast's, though, you can override it
like this::

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

The final step is :doc:`part_3`
