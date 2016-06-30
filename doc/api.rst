=================
Developer's Guide
=================


-------
Testing
-------

You can test the module integration-testing-style by simply executing::

    $ python -m feedgen

When working on this project, you should run the unit tests as well as the
integration test, like this::

    $ make test

The unit tests reside in ``feedgen/tests`` and are written using the
:mod:`unittest` module.


-----------------
API Documentation
-----------------

:class:`feedgen.feed.Podcast` (available as ``feedgen.Podcast``) is the corner
stone of PodcastGenerator. You create one instance of it for each feed you want
to make.

When you create episodes for a Podcast, you're most likely creating new
instances of :class:`feedgen.item.BaseEpisode`.

You use :class:`feedgen.person.Person` whenever an attribute is to represent
a person or an entity.

:mod:`feedgen.util` provides utility functions for the rest of the library,
and is therefore not relevant for users.


.. toctree::
   :maxdepth: 2
   :hidden:

   api.feed
   api.item
   api.person
   api.util
