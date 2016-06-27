============
Introduction
============


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


-------
License
-------
PodcastGenerator is licensed under the terms of both the FreeBSD license and the LGPLv3+.
Choose the one which is more convenient for you. For more details, have a look
at license.bsd and license.lgpl.

