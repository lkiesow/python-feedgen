=================
Developer's Guide
=================


-------
Testing
-------

You can test the module integration-testing-style by simply executing::

    $ python -m podgen

When working on this project, you should run the unit tests as well as the
integration test, like this::

    $ make test

The unit tests reside in ``podgen/tests`` and are written using the
:mod:`unittest` module.


-----------------
API Documentation
-----------------

.. autosummary::

   podgen.Podcast
   podgen.Episode
   podgen.Person
   podgen.Media
   podgen.Category
   podgen.util

.. toctree::
   :maxdepth: 2
   :hidden:

   api.podcast
   api.episode
   api.person
   api.media
   api.category
   api.util
