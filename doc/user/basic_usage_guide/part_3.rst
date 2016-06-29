
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

This concludes the basic usage guide. You might want to look at the
:doc:`../example` or the :doc:`/api`.
