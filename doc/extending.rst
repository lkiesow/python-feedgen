Adding new tags
===============

Are there XML tags you want to use that aren't supported by PodGen? If so, you
should be able to add them in using inheritance.

.. note::

   There hasn't been a focus on making it easy to extend PodGen.
   Future versions may provide better support for this.

.. note::

   Feel free to add a feature request to GitHub Issues if you think PodGen
   should support a certain tag out of the box.


Quick How-to
------------

#. Create new class that extends Podcast.
#. Add the new attribute.
#. Override :meth:`.Podcast._create_rss`, call super()._create_rss(),
   add the new tag to its result and return the new tree.

If you'll use RSS elements from another namespace, you must make sure you
update the _nsmap attribute of Podcast (you cannot define new namespaces from
an episode!). It is a dictionary with the prefix as key and the
URI for that namespace as value. To use a namespace, you must put the URI inside
curly braces, with the tag name following right after (outside the braces).
For example::

    "{%s}link" % self._nsmap['atom']  # This will render as atom:link

The `lxml API documentation`_ is a pain to read, so just look at the source code
for PodGen to figure out how to do things. The example below may help, too.

.. _lxml API documentation: http://lxml.de/api/index.html

You can do the same with Episode, if you replace _create_rss() with
rss_entry() above.

Example: Adding a ttl field
---------------------------

The examples here assume version 3 of Python is used.

Using traditional inheritance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    from lxml import etree

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

        @property
        def ttl(self):
            """Your suggestion for how many minutes podcatchers should wait
            before refreshing the feed.

            ttl stands for "time to live".

            :type: :obj:`int`
            :RSS: ttl
            """
            return self.__ttl

        @ttl.setter
        def ttl(self, ttl):
            try:
                ttl_int = int(ttl)
            except ValueError:
                raise TypeError("ttl expects an integer, got %s" % ttl)

            if ttl_int < 0:
                raise ValueError("Negative ttl values aren't accepted, got %s"
                                 % ttl_int)
            self.__ttl = ttl_int

        def _create_rss(self):
            rss = super()._create_rss()
            channel = rss.find("channel")
            if self.__ttl is not None:
                ttl = etree.SubElement(channel, 'ttl')
                ttl.text = str(self.__ttl)

            return rss

    # How to use the new class (normally, you would put this somewhere else)
    myPodcast = PodcastWithTtl(name="Test", website="http://example.org",
                               explicit=False, description="Testing ttl")
    myPodcast.ttl = 90
    print(myPodcast)


Using mixins
^^^^^^^^^^^^

To use mixins, you cannot make the class with the ttl functionality inherit
Podcast. Instead, it must inherit nothing. Other than that, the code will be
the same, so it doesn't make sense to repeat it here.

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
PodcastWithTtl, then TtlMixin, finally Podcast. This is also the order the
methods are called when chained together using super(). If you had Podcast
first, Podcast's _create_rss() method would be run first, and since it never
calls super()._create_rss(), the TtlMixin's _create_rss would never be run.
Therefore, you should always have Podcast last in that list.

Which approach is best?
^^^^^^^^^^^^^^^^^^^^^^^

The advantage of mixins isn't really displayed here, but it will become
apparent as you add more and more extensions. Say you define 5 different mixins,
which all add exactly one more attribute to Podcast. If you used traditional
inheritance, you would have to make sure each of those 5 subclasses made up a
tree. That is, class 1 would inherit Podcast. Class 2 would have to inherit
class 1, class 3 would have to inherit class 2 and so on. If two of the classes
had the same superclass, you would be screwed.

By using mixins, you can put them together however you want. Perhaps for one
podcast you only need ttl, while for another podcast you want to use the
textInput element in addition to ttl, and another podcast requires the
textInput element together with the comments element. Using traditional
inheritance, you would have to duplicate code for textInput in two classes. Not
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

If the list of attributes you want to use varies between different podcasts,
mixins are the way to go. On the other hand, mixins are overkill if you are okay
with one giant class with all the attributes you need.
