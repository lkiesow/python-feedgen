
Adding episodes
---------------

To add episodes to a feed, you need to create new
:class:`podgen.Episode` objects and
append them to the list of episodes in the Podcast. That is pretty
straight-forward::

    from podgen import Podcast, Episode
    # Create the podcast (see the previous section)
    p = Podcast()
    # Create new episode
    my_episode = Episode()
    # Add it to the podcast
    p.episodes.append(my_episode)

There is a convenience method called :meth:`Podcast.add_episode <podgen.Podcast.add_episode>`
which optionally creates a new instance of :class:`~podgen.Episode`, adds it to the podcast
and returns it, allowing you to assign it to a variable::

    from podgen import Podcast
    p = Podcast()
    my_episode = p.add_episode()

If you prefer to use the constructor, there's nothing wrong with that::

    from podgen import Podcast, Episode
    p = Podcast()
    my_episode = p.add_episode(Episode())

The advantage of using the latter form is that you can pass data to the
constructor.

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

Read more:

* :attr:`~podgen.Episode.title`
* :attr:`~podgen.Episode.subtitle`
* :attr:`~podgen.Episode.summary`
* :attr:`~podgen.Episode.long_summary`


Enclosing media
^^^^^^^^^^^^^^^

Of course, this isn't much of a podcast if we don't have any
:attr:`~podgen.Episode.media` attached to it! ::

    from datetime import timedelta
    from podgen import Media
    my_episode.media = Media("http://example.com/podcast/s01e10.mp3",
                             size=17475653,
                             type="audio/mpeg",  # Optional, can be determined
                                                 # from the url
                             duration=timedelta(hours=1, minutes=2, seconds=36)
                            )

The **type** of the media file is derived from the URI ending, if you don't
provide it yourself. Even though you
technically can have file names which don't end in their actual file extension,
iTunes will use the file extension to determine what type of file it is, without
even asking the server. You must therefore make sure your media files have the
correct file extension. If you don't care about compatibility with iTunes, you
can provide the MIME type yourself.

The **duration** is also important to include for your listeners' convenience.
Without it, they won't know how long an episode is before they start downloading
and listening. It must be an instance of :class:`datetime.timedelta`.

Normally, you must specify how big the **file size** is in bytes (and the `MIME
type`_ if the file extension is unknown to iTunes), but PodGen
can send a HEAD request to the URL and retrieve the missing information
(both file size and type). This is done by calling
:meth:`Media.create_from_server_response <podgen.Media.create_from_server_response>`
instead of using the constructor directly.
You must pass in the `requests <http://docs.python-requests.org/en/master/>`_
module, so make sure it's installed. ::

    import requests
    my_episode.media = Media.create_from_server_response(
                           requests,
                           "http://example.com/podcast/s01e10.mp3",
                           duration=timedelta(hours=1, minutes=2, seconds=36)
                       )

.. note::

   The duration cannot be fetched from the server automatically.

Read more about:

* :attr:`podgen.Episode.media` (the attribute)
* :class:`podgen.Media` (the class which you use as value)

.. _MIME type: https://en.wikipedia.org/wiki/Media_type

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

Read more about :attr:`the id attribute <podgen.Episode.id>`.

Episode's publication date
^^^^^^^^^^^^^^^^^^^^^^^^^^

An episode's publication date indicates when the episode first went live. It is
used to indicate how old the episode is, and a client may say an episode is from
"1 hour ago", "yesterday", "last week" and so on. You should therefore make sure
that it matches the exact time that the episode went live, or else your listeners
will get a new episode which appears to have existed for longer than it has.

.. note::

   It is generally a bad idea to use the media file's modification date
   as the publication date. If you make your episodes some time in advance, your
   listeners will suddenly get an "old" episode in their feed!

::

   my_episode.publication_date = datetime.datetime(2016, 5, 18, 10, 0,
                                                 tzinfo=pytz.utc)

Read more about :attr:`the publication_date attribute <podgen.Episode.publication_date>`.


The Link
^^^^^^^^

If you're publishing articles along with your podcast episodes, you should
link to the relevant article. Examples can be linking to the sound on
SoundCloud or the post on your website. Usually, your
listeners expect to find the entirety of the :attr:`~podgen.Episode.summary` by following
the link. ::

    my_episode.link = "http://example.com/article/2016/05/18/Best-example"

.. note::

   If you don't have anything to link to, then that's fine as well. No link is
   better than a disappointing link.

Read more about :attr:`the link attribute <podgen.Episode.link>`.


The Authors
^^^^^^^^^^^

Normally, the attributes :attr:`Podcast.authors <podgen.Podcast.authors>`
and :attr:`Podcast.web_master <podgen.Podcast.web_master>` (if set) are
used to determine the authors of an episode. Thus, if all your episodes have
the same authors, you should just set it at the podcast level.

If an episode's list of authors differs from the podcast's, though, you can
override it like this::

     my_episode.authors = [Person("Joe Bob")]

You can even have multiple authors::

     my_episode.authors = [Person("Joe Bob"), Person("Alice Bob")]

Read more about :attr:`an episode's authors <podgen.Episode.authors>`.


Less used attributes
^^^^^^^^^^^^^^^^^^^^

::

    # Not actually implemented by iTunes; the Podcast's image is used.
    my_episode.image = "http://example.com/static/best-example.png"

    # Set it to override the Podcast's explicit attribute for this episode only.
    my_episode.explicit = False

    # Tell iTunes that the enclosed video is closed captioned.
    my_episode.is_closed_captioned = False

    # Tell iTunes that this episode should be the first episode on the store
    # page.
    my_episode.position = 1

    # Careful! This will hide this episode from the iTunes store page.
    my_episode.withhold_from_itunes = True

More details:

* :attr:`~podgen.Episode.image`
* :attr:`~podgen.Episode.explicit`
* :attr:`~podgen.Episode.is_closed_captioned`
* :attr:`~podgen.Episode.position`
* :attr:`~podgen.Episode.withhold_from_itunes`


Shortcut for filling in data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of assigning those values one at a time, you can assign them all in
one go in the constructor – just like you can with Podcast. Just use the
attribute name as the keyword::

    Episode(
        <attribute name>=<attribute value>,
        <attribute name>=<attribute value>,
        ...
    )

See also the example in :doc:`the API Documentation </api.episode>`.

--------------------------------------------------------------------------------

The final step is :doc:`part_3`.
