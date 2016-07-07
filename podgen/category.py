# -*- coding: utf-8 -*-
"""
    podgen.category
    ~~~~~~~~~~~~~~~

    This module contains Category, which represents a single iTunes category.

    :copyright: 2016, Thorben Dahl <thorben@sjostrom.no>
    :license: FreeBSD and LGPL, see license.* for more details.
"""
class Category(object):
    """Immutable class representing an iTunes category.

    See https://help.apple.com/itc/podcasts_connect/#/itc9267a2f12 for an
    overview of the available categories and their subcategories.

    .. note::

        The categories are case-insensitive, and you may escape ampersands.
        The category and subcategory will end up properly capitalized and
        with unescaped ampersands.

    Example::

        >>> from podgen import Category
        >>> c = Category("Music")
        >>> c.category
        Music
        >>> c.subcategory
        None
        >>>
        >>> d = Category("games &amp; hobbies", "Video games")
        >>> d.category
        Games & Hobbies
        >>> d.subcategory
        Video Games
    """

    _categories = {
        'Arts': ['Design', 'Fashion & Beauty', 'Food', 'Literature',
                 'Performing Arts', 'Visual Arts'],
        'Business': ['Business News', 'Careers', 'Investing',
                     'Management & Marketing', 'Shopping'],
        'Comedy': [],
        'Education': ['Education', 'Education Technology',
                      'Higher Education', 'K-12', 'Language Courses', 'Training'],
        'Games & Hobbies': ['Automotive', 'Aviation', 'Hobbies',
                            'Other Games', 'Video Games'],
        'Government & Organizations': ['Local', 'National', 'Non-Profit',
                                       'Regional'],
        'Health': ['Alternative Health', 'Fitness & Nutrition', 'Self-Help',
                   'Sexuality'],
        'Kids & Family': [],
        'Music': [],
        'News & Politics': [],
        'Religion & Spirituality': ['Buddhism', 'Christianity', 'Hinduism',
                                    'Islam', 'Judaism', 'Other', 'Spirituality'],
        'Science & Medicine': ['Medicine', 'Natural Sciences',
                               'Social Sciences'],
        'Society & Culture': ['History', 'Personal Journals', 'Philosophy',
                              'Places & Travel'],
        'Sports & Recreation': ['Amateur', 'College & High School',
                                'Outdoor', 'Professional'],
        'Technology': ['Gadgets', 'Tech News', 'Podcasting',
                       'Software How-To'],
        'TV & Film': []
    }

    def __init__(self, category, subcategory=None):
        """Create new Category object. See the class description of
        :class:´~podgen.category.Category`.

        :param category: Category of the podcast.
        :type category: str
        :param subcategory: (Optional) Subcategory of the podcast.
        :type subcategory: str or None
        """
        if not category:
            raise TypeError("category must be provided, was \"%s\"" % category)
        # Do a case-insensitive search for the category
        search_category = category.strip().replace("&amp;", "&").lower()
        for actual_category in self._categories:
            if actual_category.lower() == search_category:
                # We found it
                canonical_category = actual_category
                break
        else:  # no break
            raise ValueError('Invalid category "%s"' % category)
        self.__category = canonical_category

        # Do a case-insensitive search for the subcategory, if provided
        canonical_subcategory = None
        if subcategory is not None:
            search_subcategory = subcategory.strip().replace("&amp;", "&")\
                .lower()
            for actual_subcategory in self._categories[canonical_category]:
                if actual_subcategory.lower() == search_subcategory:
                    canonical_subcategory = actual_subcategory
                    break
            else:  # no break
                raise ValueError('Invalid subcategory "%s" under category "%s"'
                                 % (subcategory, canonical_category))

        self.__subcategory = canonical_subcategory

    @property
    def category(self):
        """The category represented by this object. Read-only.

        :type: :obj:`str`
        """
        return self.__category
        # Make this attribute read-only by not implementing setter

    @property
    def subcategory(self):
        """The subcategory this object represents. Read-only.

        :type: :obj:`str`
        """
        return self.__subcategory
        # Make this attribute read-only by not implementing setter

    def __repr__(self):
        return 'Category(category=%s, subcategory=%s)' % \
               (self.category, self.subcategory)
