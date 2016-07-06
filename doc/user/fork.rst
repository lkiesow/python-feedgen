=============
Why the fork?
=============

This project is a fork of ``python-feedgen`` which cuts away everything that
doesn't serve the goal of **making it easy and simple to generate podcasts** from
a Python program. Thus, this project includes only a **subset** of the features
of ``python-feedgen``. And I don't think anyone in their right mind would accept a pull
request which removes 70% of the features ;-) Among other things, support for ATOM and
Dublin Core is removed, and the remaining code is almost entirely rewritten.


Inspiration
-----------

The reason I felt like making such drastic changes, is that the original library is
**exceptionally hard to learn** and use. Error messages would not tell you what was wrong,
the concept of extensions is poorly explained and the methods are a bit weird, in that
they function as getters and setters at the same time. The fact that you have three
separate ways to go about setting multi-value variables, is also a bit confusing.

Perhaps the biggest problem, though, is the awkwardness that stems from enabling
RSS and ATOM feeds through the same API. In case you don't know, ATOM is a
"competitor" to RSS, and has many more capabilities than RSS. However, it is
not used for podcasting. It is confusing because some methods will map an ATOM value to
its closest sibling in RSS, some in logical ways (like the ATOM method ``rights`` setting
the value of the RSS property ``copyright``) and some differ in subtle ways (like using
(ATOM) ``logo`` versus (RSS) ``image``). Other methods are more complex (see ``link``). They're all
confusing, though, since changing one property automatically changes another implicitly.
They also cause bugs, since it is so difficult to wrap your head around how one
interact with another.
Removing ATOM fixes all these issues.

Even then, ``python-feedgen`` aims at being comprehensive, which means you must
learn the RSS and podcast standards, which include many legacy elements you
don't really need. For example, the original RSS spec
includes support for an image, but that image is required to be less than 144 pixels
wide (88 pixels being the default) and 400 pixels high (remember, this was year *2000*).
Itunes can't have any of that (understandably so), so they added their own ``itunes:image``
tag, which has its own set of requirements (images can be no smaller than 1400x1400px!).
I believe **the API should help guide the users** by hiding the legacy image tag,
and you as a user shouldn't need to know all this. You just need to know that the
image must be larger than 1400x1400 pixels, not the history behind everything.

Alignment with the philosophies
-------------------------------

``python-feedgen``'s code breaks all the philosophies listed above:

#. Beautiful is better than ugly, yet all properties are set through hybrid
   setter/getter methods.
#. Explicit is better than implicit, yet changing one property will cause
   changes to other properties implicitly.
#. Simple is better than complex, yet creating podcasts requires that you
   load an extension, and somehow figure out that this extension's methods
   are available as methods of the extension's name, which suddenly is
   available as a property of your FeedGenerator object.
#. Complex is better than complicated, yet an entire framework is built to
   handle extensions, rather than using class inheritance.
#. Readability counts, yet classes are named after their function and not what
   they represent, and (again) properties are set through methods.

In short, the **original project breaks all the idioms listed in Philosophy**, and
fixing it would require changes too big or too dramatic to be applied upstream.

Whenever a change *is* appropriate for upstream, however, we should strive to
bring it there, so it can benefit **everyone**.


Summary of changes
------------------

* ``FeedGenerator`` is renamed to :class:`~podgen.Podcast` and ``FeedItem`` is accessed
  at ``Podcast.Episode`` (or directly: :class:`~podgen.BaseEpisode`).
* Support for ATOM removed.
* Move from using getter and setter methods to using properties, which you can
  assign just like you would assign any other property.

  * Compound values (like managingEditor or enclosure) use
    classes now.

* Remove support for some uncommon elements:

  * ttl
  * category
  * image
  * itunes:summary
  * rating
  * textInput

* Rename the remaining properties so their names don't necessarily match the RSS
  elements they map to. Instead, the names should be descriptive and easy to
  understand.
* Add shorthand for generating the RSS: Just try to converting your :class:`~podgen.Podcast`
  object to :obj:`str`!
* Improve the documentation
