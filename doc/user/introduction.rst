============
Introduction
============


----------
Philosophy
----------

This project is heavily inspired by the wonderful
`Kenneth Reitz <http://www.kennethreitz.org/projects>`_, known for the
`Requests <http://docs.python-requests.org>`_ library, which features an API which is
as beautiful as it is effective. Watching his
`"Documentation is King" talk <http://www.kennethreitz.org/talks/#/documentation-is-king/>`_,
I wanted to make some of the libraries I'm using suitable for use by actual humans.

This project is to be developed following the same
`PEP 20 <https://www.python.org/dev/peps/pep-0020/>`_ idioms as
`Requests <http://docs.python-requests.org/en/master/user/intro/#philosophy>`_:

1. Beautiful is better than ugly.
2. Explicit is better than implicit.
3. Simple is better than complex.
4. Complex is better than complicated.
5. Readability counts.

To enable this, the project focuses on one task alone: making it easy to generate a podcast.

-----
Scope
-----

This library does NOT help you publish a podcast, or manage podcasts. It's just
a tool that takes information about your podcast, and outputs an RSS feed which
you can then publish however you want.

Both the process of getting information
about your podcast, and publishing it needs to be done by you. Even then,
it will save you from hammering your head over confusing and undocumented APIs
and conflicting views on how different RSS elements should be used. It also
saves you from reading the RSS specification, the RSS Best Practices and the
documentation for iTunes' Podcast Connect.

PodcastGenerator is geared towards developers who aren't super familiar with
RSS and XML. If you know exactly how you want the XML to look, then you're
better off using a template engine like Jinja2 (even if friends don't let
friends touch XML bare-handed).

-------
License
-------
PodcastGenerator is licensed under the terms of both the FreeBSD license and the LGPLv3+.
Choose the one which is more convenient for you. For more details, have a look
at license.bsd and license.lgpl.

