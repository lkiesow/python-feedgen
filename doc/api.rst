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

.. autosummary::

   feedgen.Podcast
   feedgen.Episode
   feedgen.Person
   feedgen.Media
   feedgen.Category
   feedgen.util

.. toctree::
   :maxdepth: 2
   :hidden:

   api.podcast
   api.episode
   api.person
   api.media
   api.category
   api.util
