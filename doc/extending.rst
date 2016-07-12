Adding new tags
===============

Are there XML elements you want to use that aren't supported by PodGen? If so,
you should be able to add them in using inheritance.

.. warning::

   This is an advanced topic.

.. note::

   There hasn't been a focus on making it easy to extend PodGen.
   Future versions may provide better support for this.

.. note::

   Feel free to add a feature request to `GitHub Issues`_ if you think PodGen
   should support a certain element out of the box.

.. _GitHub Issues: https://github.com/tobinus/python-podgen/issues


Quick How-to
------------

#. Create new class that extends :class:`.Podcast`.
#. Add the new attribute.
#. Override :meth:`~.Podcast._create_rss`, call ``super()._create_rss()``,
   add the new element to its result and return the new tree.

You can do the same with :class:`.Episode`, if you replace
:meth:`~.Podcast._create_rss` with :meth:`~Episode.rss_entry` above.

There are plenty of small quirks you have to keep in mind. You are strongly
encouraged to read the example below.

Using namespaces
^^^^^^^^^^^^^^^^

If you'll use RSS elements from another namespace, you must make sure you
update the :attr:`~.Podcast._nsmap` attribute of :class:`.Podcast`
(you cannot define new namespaces from an episode!). It is a dictionary with the
prefix as key and the URI for that namespace as value. To use a namespace, you
must put the URI inside curly braces, with the tag name following right after
(outside the braces). For example::

    "{%s}link" % self._nsmap['atom']  # This will render as atom:link

The `lxml API documentation`_ is a pain to read, so just look at the `source code
for PodGen`_ and the example below.

.. _lxml API documentation: http://lxml.de/api/index.html
.. _source code for PodGen: https://github.com/tobinus/python-podgen/blob/master/podgen/podcast.py

Example: Adding a ttl element
-----------------------------

The examples here assume version 3 of Python is used.

``ttl`` is an RSS element and stands for "time to live", and can only be an
integer which indicates how many minutes the podcatcher can rely on its copy of
the feed before refreshing (or something like that). There is confusion as to
what it is supposed to mean (max refresh frequency? min refresh frequency?),
which is why it is not included in PodGen. If you use it, you should treat it as
the **recommended** update period (source: `RSS Best Practices`_).

.. _RSS Best Practices: http://www.rssboard.org/rss-profile#element-channel-ttl

Using traditional inheritance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    # The module used to create the XML tree and generate the XML
    from lxml import etree

    # The class we will extend
    from podgen import Podcast


    class PodcastWithTtl(Podcast):
        """This is an extension of Podcast, which supports ttl.

        You gain access to ttl by creating a new instance of this class instead
        of Podcast.
        """
        def __init__(self, *args, **kwargs):
            # Initialize the ttl value
            self.__ttl = None

            # Has the user passed in ttl value as a keyword?
            if 'ttl' in kwargs:
                self.ttl = kwargs['ttl']
                kwargs.pop('ttl')  # avoid TypeError from super()

            # Call Podcast's constructor
            super().__init__(*args, **kwargs)

            # If we were to use another namespace, we would add this here:
            # self._nsmap['prefix'] = "URI"

        @property
        def ttl(self):
            """Your suggestion for how many minutes podcatchers should wait
            before refreshing the feed.

            ttl stands for "time to live".

            :type: :obj:`int`
            :RSS: ttl
            """
            # By using @property and @ttl.setter, we encapsulate the ttl field
            # so that we can check the value that is assigned to it.
            # If you don't need this, you could just rename self.__ttl to
            # self.ttl and remove those two methods.
            return self.__ttl

        @ttl.setter
        def ttl(self, ttl):
            # Try to convert to int
            try:
                ttl_int = int(ttl)
            except ValueError:
                raise TypeError("ttl expects an integer, got %s" % ttl)
            # Is this negative?
            if ttl_int < 0:
                raise ValueError("Negative ttl values aren't accepted, got %s"
                                 % ttl_int)
            # All checks passed
            self.__ttl = ttl_int

        def _create_rss(self):
            # Let Podcast generate the lxml etree (adding the standard elements)
            rss = super()._create_rss()
            # We must get the channel element, since we want to add subelements
            # to it.
            channel = rss.find("channel")
            # Only add the ttl element if it has been populated.
            if self.__ttl is not None:
                # First create our new subelement of channel.
                ttl = etree.SubElement(channel, 'ttl')
                # If we were to use another namespace, we would instead do this:
                # ttl = etree.SubElement(channel,
                #                        '{%s}ttl' % self._nsmap['prefix'])

                # Then, fill it with the ttl value
                ttl.text = str(self.__ttl)

            # Return the new etree, now with ttl
            return rss

    # How to use the new class (normally, you would put this somewhere else)
    myPodcast = PodcastWithTtl(name="Test", website="http://example.org",
                               explicit=False, description="Testing ttl")
    myPodcast.ttl = 90  # or set ttl=90 in the constructor
    print(myPodcast)


Using mixins
^^^^^^^^^^^^

To use mixins, you cannot make the class with the ``ttl`` functionality inherit
:class:`.Podcast`. Instead, it must inherit nothing. Other than that, the code
will be the same, so it doesn't make sense to repeat it here.

::

    class TtlMixin(object):
        # ...

    # How to use the new mixin
    class PodcastWithTtl(TtlMixin, Podcast):
        def __init__(*args, **kwargs):
            super().__init__(*args, **kwargs)

    myPodcast = PodcastWithTtl(name="Test", website="http://example.org",
                               explicit=False, description="Testing ttl")
    myPodcast.ttl = 90
    print(myPodcast)

Note the order of the mixins in the class declaration. You should read it as
the path Python takes when looking for a method. First Python checks
``PodcastWithTtl``, then ``TtlMixin`` and finally :class:`.Podcast`. This is
also the order the methods are called when chained together using :func:`super`.
If you had Podcast first, :meth:`.Podcast._create_rss` method would be run
first, and since it never calls ``super()._create_rss()``, the ``TtlMixin``'s
``_create_rss`` would never be run. Therefore, you should always have
:class:`.Podcast` last in that list.

Which approach is best?
^^^^^^^^^^^^^^^^^^^^^^^

The advantage of mixins isn't really displayed here, but it will become
apparent as you add more and more extensions. Say you define 5 different mixins,
which all add exactly one more element to :class:`.Podcast`. If you used traditional
inheritance, you would have to make sure each of those 5 subclasses made up a
tree. That is, class 1 would inherit :class:`.Podcast`. Class 2 would have to inherit
class 1, class 3 would have to inherit class 2 and so on. If two of the classes
had the same superclass, you could get screwed.

By using mixins, you can put them together however you want. Perhaps for one
podcast you only need ``ttl``, while for another podcast you want to use the
``textInput`` element in addition to ``ttl``, and another podcast requires the
``textInput`` element together with the ``comments`` element. Using traditional
inheritance, you would have to duplicate code for ``textInput`` in two classes. Not
so with mixins::

    class PodcastWithTtl(TtlMixin, Podcast):
        def __init__(*args, **kwargs):
            super().__init__(*args, **kwargs)

    class PodcastWithTtlAndTextInput(TtlMixin, TextInputMixin, Podcast):
        def __init__(*args, **kwargs):
            super().__init__(*args, **kwargs)

    class PodcastWithTextInputAndComments(TextInputMixin, CommentsMixin,
                                          Podcast):
        def __init__(*args, **kwargs):
            super().__init__(*args, **kwargs)

If the list of elements you want to use varies between different podcasts,
mixins are the way to go. On the other hand, mixins are overkill if you are okay
with one giant class with all the elements you need.
