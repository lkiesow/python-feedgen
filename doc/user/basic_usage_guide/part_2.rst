
Adding episodes
---------------

To add episodes to a feed, you need to create new
:class:`feedgen.episode.Episode` objects and
append them to the list of entries in the Podcast. That is pretty
straight-forward::

    from feedgen.episode import Episode
    my_episode = Episode()
    p.episodes.append(my_episode)

There is a convenience method called :meth:`Podcast.add_episode <feedgen.podcast.Podcast.add_episode>`
which optionally creates a new instance of :class:`~feedgen.episode.Episode`, adds it to the podcast
and returns it, allowing you to assign it to a variable::

    my_episode = p.add_episode()

If you prefer to use the constructor, there's nothing wrong with that::

    my_episode = p.add_episode(Episode())

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

   ~feedgen.episode.BaseEpisode.title
   ~feedgen.episode.BaseEpisode.subtitle
   ~feedgen.episode.BaseEpisode.summary
   ~feedgen.episode.BaseEpisode.long_summary


Enclosing media
^^^^^^^^^^^^^^^

Of course, this isn't much of a podcast if we don't have any **media**
attached to it! ::

    from datetime import timedelta
    my_episode.media = Media("http://example.com/podcast/s01e10.mp3",
                             size=17475653,
                             type="audio/mpeg",  # Optional, can be determined
                                                 # from the url
                             duration=timedelta(hours=1, minutes=2, seconds=36)
                            )

Normally, you must specify how big the **file size** is in bytes (and the MIME
type, if the file extension is unknown to iTunes), but PodcastGenerator
can send a HEAD request to the URL and retrieve the missing information. This is
done by calling :meth:`Media.create_from_server_response <feedgen.media.Media.create_from_server_response>`
instead of using the constructor directly.
You must pass in the `requests <http://docs.python-requests.org/en/master/>`_
module, so it must be installed! ::

    import requests
    my_episode.media = Media.create_from_server_response(
                           requests,
                           "http://example.com/podcast/s01e10.mp3",
                           duration=timedelta(hours=1, minutes=2, seconds=36)
                       )


The **type** of the media file is derived from the URI ending. Even though you
technically can have file names which don't end in their actual file extension,
iTunes will use the file extension to determine what type of file it is, without
even asking the server. You must therefore make sure your media files have the
correct file extension. If you don't care about compatibility with iTunes, you
can provide the MIME type yourself.

The **duration** is also important to include, for your listeners' convenience.
Without it, they won't know how long an episode is before they start downloading
and listening.

.. autosummary::

   ~feedgen.episode.BaseEpisode.media
   ~feedgen.media.Media


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

.. autosummary:: ~feedgen.episode.BaseEpisode.id


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

   my_episode.publication_date = datetime.datetime(2016, 5, 18, 10, 0,
                                                 tzinfo=pytz.utc)

.. autosummary:: ~feedgen.episode.BaseEpisode.publication_date


The Link
^^^^^^^^

If you're publishing articles along with your podcast episodes, you should
link to the relevant article. Examples can be linking to the sound on
SoundCloud or the post on your website. Usually, your
listeners expect to find the entirety of the :attr:`~feedgen.episode.BaseEpisode.summary` by following
the link. ::

    my_episode.link = "http://example.com/article/2016/05/18/Best-example"

.. note::

   If you don't have anything to link to, then that's fine as well. No link is
   better than a disappointing link.

.. autosummary:: ~feedgen.episode.BaseEpisode.link


The Authors
^^^^^^^^^^^

.. note::

   Some of those attributes correspond to attributes found in
   :class:`~feedgen.podcast.Podcast`. In such cases, you should only set those
   attributes at the episode level if they **differ** from their value at the
   podcast level.

Normally, the attributes :attr:`Podcast.authors <feedgen.podcast.Podcast.authors>`
and :attr:`Podcast.web_master <feedgen.podcast.Podcast.web_master>` (if set) are
used to determine the authors of an episode. Thus, if all your episodes have
the same authors, you should just set it at the podcast level.

If an episode's authors differs from the podcast's, though, you can override it
like this::

     my_episode.authors = [Person("Joe Bob")]

You can even have multiple authors::

     my_episode.authors = [Person("Joe Bob"), Person("Alice Bob")]

.. autosummary:: ~feedgen.episode.BaseEpisode.authors


Less used attributes
^^^^^^^^^^^^^^^^^^^^

::

    my_episode.image = "http://example.com/static/best-example.png"
    my_episode.explicit = False
    my_episode.is_closed_captioned = False  # Only applicable for video
    my_episode.position = 1
    # Be careful about using the following attribute!
    my_episode.withhold_from_itunes = True

.. autosummary::

   ~feedgen.episode.BaseEpisode.image
   ~feedgen.episode.BaseEpisode.explicit
   ~feedgen.episode.BaseEpisode.is_closed_captioned
   ~feedgen.episode.BaseEpisode.position
   ~feedgen.episode.BaseEpisode.withhold_from_itunes

The final step is :doc:`part_3`
