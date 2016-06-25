==============================================
Feedgenerator (forked) - Podcasting for humans
==============================================

Ignore:
[![Build Status](https://travis-ci.org/lkiesow/python-feedgen.svg?branch=master)
](https://travis-ci.org/lkiesow/python-feedgen)

**Note: This document is in the process of being rewritten.**

This module can be used to generate podcast feeds in RSS format.

It is licensed under the terms of both, the FreeBSD license and the LGPLv3+.
Choose the one which is more convenient for you. For more details have a look
at license.bsd and license.lgpl.

More details about the project:

- Repository:            https://github.com/lkiesow/python-feedgen
- Documentation:         http://lkiesow.github.io/python-feedgen/
- Python Package Index:  https://pypi.python.org/pypi/feedgen/


------------
Installation
------------

Currently, you'll need to clone this repository, and create a virtualenv and
install lxml and dateutils.


-------------
Create a Feed
-------------

To create a feed simply instantiate the Podcast class and insert some
data::

    >>> from feedgen.feed import Podcast
    >>> fg = Podcast()
    >>> fg.title('Some Testfeed')
    >>> fg.author( {'name':'John Doe','email':'john@example.de'} )
    >>> fg.link( href='http://example.com', rel='alternate' )
    >>> fg.image('http://ex.com/logo.jpg')
    >>> fg.description('This is a cool feed!')
    >>> fg.link( href='http://larskiesow.de/test.atom')
    >>> fg.language('en')

Note that for the methods which set fields that can occur more than once in a
feed you can use all of the following ways to provide data:

- Provide the data for that element as keyword arguments
- Provide the data for that element as dictionary
- Provide a list of dictionaries with the data for several elements

Example::

    >>> fg.contributor( name='John Doe', email='jdoe@example.com' )
    >>> fg.contributor({'name':'John Doe', 'email':'jdoe@example.com'})
    >>> fg.contributor([{'name':'John Doe', 'email':'jdoe@example.com'}, ...])

-----------------
Generate the Feed
-----------------

After that you can generate RSS by calling:

    >>> rssfeed  = fg.rss_str(pretty=True) # Get the RSS feed as string
    >>> fg.rss_file('rss.xml') # Write the RSS feed to a file


----------------
Add Feed Entries
----------------

To add entries (items) to a feed you need to create new BaseEpisode objects and
append them to the list of entries in the Podcast. The most convenient
way to go is to use the Podcast itself for the instantiation of the
BaseEpisode object:

    >>> fe = fg.add_episode()
    >>> fe.id('http://lernfunk.de/media/654321/1')
    >>> fe.title('The First BaseEpisode')

The FeedGenerators method `add_episode(...)` without argument provides will
automatically generate a new BaseEpisode object, append it to the feeds internal
list of entries and return it, so that additional data can be added.

--------------------------
Using the podcast features
--------------------------

Most iTunes-specific features are available as methods that start with `itunes_`,
although most features are platform agnostic.

    >>> from feedgen.feed import Podcast
    >>> fg = Podcast()
    ...
    >>> fg.itunes_category('Technology', 'Podcasting')
    ...
    >>> fe = fg.add_episode()
    >>> fe.id('http://lernfunk.de/media/654321/1/file.mp3')
    >>> fe.title('The First Episode')
    >>> fe.description('Enjoy our first episode.')
    >>> fe.enclosure('http://lernfunk.de/media/654321/1/file.mp3', 0, 'audio/mpeg')
    ...
    >>> fg.rss_str(pretty=True)
    >>> fg.rss_file('podcast.xml')



---------------------
Testing the Generator
---------------------

You can test the module integration-testing-style by simply executing::

    $ python -m feedgen

If you want to have a look at the code for this test to have a working code
example for a whole feed generation process, you can find it in the
[`__main__.py`](https://github.com/tobinus/python-feedgen/blob/podcastgen/feedgen/__main__.py).


----------
Philosophy
----------

This project is heavily inspired by the wonderful
[Kenneth Reitz](http://www.kennethreitz.org/projects), known for the
[Requests](http://docs.python-requests.org) library, which features an API which is
as beautiful as it is effective. Watching his
["Documentation is King" talk](http://www.kennethreitz.org/talks/#/documentation-is-king/),
I wanted to make some of the libraries I'm using suitable for use by actual humans.

This project is to be developed following the same
[PEP 20](https://www.python.org/dev/peps/pep-0020/) idioms as
[Requests](http://docs.python-requests.org/en/master/user/intro/#philosophy):

1. Beautiful is better than ugly.
2. Explicit is better than implicit.
3. Simple is better than complex.
4. Complex is better than complicated.
5. Readability counts.

To enable this, the project focuses on one task alone: making it easy to generate a podcast.


-------------
Why the fork?
-------------

This project is a fork of `python-feedgen` which cuts away everything that
doesn't serve the goal of **making it easy and simple to generate podcasts** from
a Python program. **Thus, this project includes only a subset of the features
of `python-feedgen`**. And I don't think anyone in their right mind would accept a pull
request which removes 70% of the features ;-) Among other things, support for ATOM and
Dublin Core is removed, and the remaining code is almost entirely rewritten.

The reason I felt like making such drastic changes, is that the original library is
**exceptionally hard to learn** and use. Error messages would not tell you what was wrong,
the concept of extensions is poorly explained and the methods are a bit weird, in that
they function as getters and setters at the same time. The fact that you have three
separate ways to go about setting multi-value variables, is also a bit confusing.

Perhaps the biggest problem, though, is the awkwardness that stems from enabling
RSS and ATOM feeds through the same API. Some methods will map an ATOM value to
its closest sibling in RSS, some in logical ways (like the ATOM method `rights` setting
the value of the RSS property `copyright`) and some differ in subtle ways (like using
(ATOM) `logo` versus (RSS) `image`). Other methods are more complex (see `link`). They're all
confusing, though, since changing one property automatically changes another implicitly.
Removing ATOM (or RSS for that matter) fixes all these issues.

Even then, the RSS specs and iTunes' podcast recommendations are sometimes able to
cause confusion on their own, especially for those of us who don't have time to
read both specifications from start to end. For example, the original RSS spec
includes support for an image, but that image is required to be less than 144 pixels
wide (88 pixels being the default) and 400 pixels high (remember, this was year _2000_).
Itunes can't have any of that (understandably so), so they added their own `itunes:image`
tag, which has its own set of requirements (images can be no smaller than 1400x1400px!).
I believe **the API should help guide the users** by hiding the legacy image tag,
and gently push users towards the iTunes tag used today.

In short, the **original project breaks all the idioms listed in Philosophy**, and
fixing it would require changes too big or too dramatic to be applied upstream.
Whenever a change _is_ appropriate for upstream, however, we should strive to
bring it there, so it can benefit **everyone**.
