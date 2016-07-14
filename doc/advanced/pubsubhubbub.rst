Using PubSubHubbub
==================

PubSubHubbub is a free and open protocol for pushing updates to clients
when there's new content available in the feed, as opposed to the traditional
polling clients do.

Read about `what PubSubHubbub is`_ before you continue.

.. _what PubSubHubbub is: https://en.wikipedia.org/wiki/PubSubHubbub

.. note::

   While the protocol supports having multiple PubSubHubbub hubs for a single
   Podcast, there is no support for this in PodGen at the moment.

.. warning::

   Read through the whole guide at least once before you start implementing
   this. Specifically, you must *not* set the :attr:`~.Podcast.pubsubhubbub`
   attribute if you haven't got a way to notify hubs of new episodes.

--------------------------------------------------------------------------------

.. contents::
   :backlinks: none


Step 1: Set feed_url
--------------------

First, you must ensure that the :class:`.Podcast` object has the
:attr:`~.Podcast.feed_url` attribute set to the URL at which the feed is
accessible.

::

    # Assume p is a Podcast object
    p.feed_url = "https://example.com/feeds/examplefeed.rss"

Step 2: Decide on a hub
-----------------------

The `Wikipedia article`_ mentions a few options you can use (called Community
Hosted hub providers). Alternatively, you can set up and host your own server
using one of the open source alternatives, like for instance `Switchboard`_.

.. _Wikipedia article: https://en.wikipedia.org/wiki/PubSubHubbub#Usage
.. _Switchboard: https://github.com/aaronpk/Switchboard

Step 3: Set pubsubhubbub
------------------------

The Podcast must contain information about which hub to use. You do this by
setting :attr:`~.Podcast.pubsubhubbub` to the URL which the hub is available at.

::

    p.pubsubhubbub = "https://pubsubhubbub.example.com/"

Step 4: Set HTTP Link Header
----------------------------

In addition to embedding the PubSubHubbub hub URL and the feed's URL in the
RSS itself, you should use the
`Link header`_ in the HTTP response that is sent with this feed,
duplicating the link to the PubSubHubbub and the feed. Example of
what it might look like:

.. code-block:: none

   Link: <https://link.to.pubsubhubbub.example.org/>; rel="hub",
         <https://example.org/podcast.rss>; rel="self"

How you can achieve this varies from framework to framework. Here is an example
using `Flask`_ (assuming the code is inside a view function)::

    from flask import make_response
    from podgen import Podcast
    # ...
    @app.route("/<feedname>")  # Just as an example
    def show_feed(feedname):
        p = Podcast()
        # ...
        # This is the relevant part:
        response = make_response(str(p))
        response.headers.add("Link", "<%s>" % p.pubsubhubbub, rel="hub")
        response.headers.add("Link", "<%s>" % p.feed_url, rel="self")
        return response

This is necessary for compatibility with the different versions of
PubSubHubbub. The `latest version of the standard`_ specifically says
that publishers MUST use the Link header. If you're unable to do this, you
can try publishing the feed without; most clients and hubs should manage
just fine.

.. _Link header: https://tools.ietf.org/html/rfc5988#page-6
.. _latest version of the standard: http://pubsubhubbub.github.io/PubSubHubbub/pubsubhubbub-core-0.4.html#rfc.section.4
.. _Flask: http://flask.pocoo.org/

Step 5: Notify the hub of new episodes
--------------------------------------

.. warning::

   The hub won't know that you've published new episodes unless you tell it about
   it. If you don't do this, the hub will assume there is no new content, and
   clients which trust the hub to inform them of new episodes will think there
   is no new content either. **Don't set the pubsubhubbub field if you haven't set
   this up yet.**

Different hubs have different ways of notifying it of new episodes. That's why
you must notify the hubs yourself; supporting all hubs is out of scope for
PodGen.

If you use the `Google PubSubHubbub`_ or the `Superfeedr hub`_, there is a
pip package called `PubSubHubbub_Publisher`_ which provides this functionality
for you. Example::

    from pubsubhubbub_publish import publish, PublishError
    from podgen import Podcast
    # ...
    try:
        publish(p.pubsubhubbub, p.feed_url)
    except PublishError as e:
        # Handle error

In all other cases, you're encouraged to use `Requests`_ to make the necessary
`POST request`_ (if no publisher package is available).

.. note::

   If you have changes in multiple feeds, you can usually send just one single
   notification to the hub with all the feeds' URLs included. It is worth
   researching, as it can save both you and the hub a lot of time.

.. _Google PubSubHubbub: https://pubsubhubbub.appspot.com/
.. _Superfeedr hub: https://pubsubhubbub.superfeedr.com/
.. _PubSubHubbub_Publisher: https://pypi.python.org/pypi/PubSubHubbub_Publisher
.. _Requests: http://docs.python-requests.org
.. _POST request: http://docs.python-requests.org/en/master/user/quickstart/#make-a-request
