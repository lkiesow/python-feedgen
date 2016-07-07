
Generating the RSS
------------------

Once you've added all the information and episodes, you're ready to
take the final step::

    rssfeed = p.rss_str()
    # Print to stdout, just as an example
    print(rssfeed)

If you're okay with the default parameters of :meth:`podgen.Podcast.rss_str`,
you can use a shortcut by converting your :class:`~podgen.Podcast` to :obj:`str`::

    rssfeed = str(p)
    print(rssfeed)
    # Or let print convert to str for you
    print(p)

.. autosummary::

    ~podgen.Podcast.rss_str

You may also write the feed to a file directly, using :meth:`podgen.Podcast.rss_file`::

    p.rss_file('rss.xml', minimize=True)


.. autosummary::

    ~podgen.Podcast.rss_file

.. note::

   If there are any mandatory attributes that aren't set, you'll get errors
   when generating the RSS.

.. note::

   Generating the RSS is not completely free. Save the result to a variable
   once instead of generating the same RSS over and over.
