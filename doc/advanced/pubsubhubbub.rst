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
using one of the implementations found at the `official PubSubHubbub project
page`_.

.. _Wikipedia article: https://en.wikipedia.org/wiki/PubSubHubbub#Usage
.. _official PubSubHubbub project page: https://github.com/pubsubhubbub

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
using Flask (assuming the code is inside a view function)::

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

Step 5: Publish the changes
---------------------------

Ensure the changes above are published before proceeding. That is, if a client
downloads the feed, it should receive the Link headers and the pubsubhubbub
and feed_url contents.

Step 6: Notify the hub of new episodes
--------------------------------------

.. note::

   PodGen does not contain any logic for figuring out whether a Podcast has
   changed or not. You must do that part yourself.

PodGen has two convenience methods that you can use to notify the hub you chose
of any additions made to the feed. The way this works, is that you say to the
hub "Hey, we've made additions to this feed", and the hub looks at the feed and
determines what is new, and sends the new episode(s) to any subscribed clients.

There are three pre-requisites for using those methods:

#. The `Requests`_ module has been installed.
#. The :class:`.Podcast` object must have :attr:`~.Podcast.pubsubhubbub` and
   :attr:`~.Podcast.feed_url` set.
#. The new episodes will be included in the feed if someone requests the feed
   at the moment the methods are called.

   * If this isn't true, the hub will always be lagging one change behind!

.. _Requests: http://docs.python-requests.org

One of the methods work best when only one feed has changed. The other one can
handle both the case where one feed has changed, and the case where multiple
feeds have changed.

.. autosummary::
   podgen.Podcast.notify_hub
   podgen.Podcast.notify_multiple

Example where one Podcast has changed::

    import requests
    from podgen import Podcast
    # ...
    p.notify_hub(requests)

Example where multiple Podcasts have changed::

    import requests
    from podgen import Podcast
    # ...
    changed_podcasts = [
        # ... multiple Podcast objects here
    ]
    Podcast.notify_multiple(requests, changed_podcasts)

Always use the latter form when multiple Podcasts have changed; you'll save
lots of time since only one request needs to be made per hub.
