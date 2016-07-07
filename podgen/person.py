# -*- coding: utf-8 -*-
"""
    podgen.person
    ~~~~~~~~~~~~~

    This file contains the Person class, which is used to represent a person or
    an entity.

    :copyright: 2016, Thorben Dahl <thorben@sjostrom.no>
    :license: FreeBSD and LGPL, see license.* for more details.
"""
class Person(object):
    """Data-oriented class representing a single person or entity.

    A Person can represent both real persons and less personal entities like
    organizations. Example::

        >>> p.authors = [Person("Example Radio", "mail@example.org")]

    .. note::

        At any time, one of name or email must be present.
        Both cannot be None or empty at the same time.

    .. warning::

        **Any names and email addresses** you put into a Person object will
        eventually be included and **published** together with
        the feed. If you want to keep a name or email address private, then you
        must make sure it isn't used in a Person object (or to be precise: that
        the Person object with the name or email address isn't used in any
        Podcast or Episode.)

    Example of use::

        >>> from podgen import Person
        >>> Person("John Doe")
        Person(name=John Doe, email=None)
        >>> Person(email="johndoe@example.org")
        Person(name=None, email=johndoe@example.org)
        >>> Person()
        ValueError: You must provide either a name or an email address.

    """

    def __init__(self, name=None, email=None):
        """Create new person with a name, email or both.

        You don't need to provide both a name and an email, but you must
        provide one of them.

        :param name: This person's name.
        :type name: str or None
        :param email: This person's email address. The address it made public
            when the feed is published, so be careful about adding a personal
            email address here. The spambots are always on lookout!
        :type email: str or None

        """
        if not self._is_valid(name, email):
            raise ValueError("You must provide either a name or an email "
                             "address.")
        self.__name = name
        self.__email = email

    def _is_valid(self, name, email):
        """Check whether one of name and email are usable."""
        return name or email

    @property
    def name(self):
        """This person's name.

        :type: :obj:`str`
        """
        return self.__name

    @name.setter
    def name(self, new_name):
        if not self._is_valid(new_name, self.email):
            raise ValueError("The name or email must be present at any time, "
                             "cannot set name to \"%s\" as long as email is "
                             "\"%s\"" % (new_name, self.email))
        self.__name = new_name

    @property
    def email(self):
        """This person's public email address.

        :type: :obj:`str`
        """
        return self.__email

    @email.setter
    def email(self, new_email):
        if not self._is_valid(self.name, new_email):
            raise ValueError("The name or email must be present at any time, "
                             "cannot set email to \"%s\" as long as name is "
                             "\"%s\"" % (new_email, self.name))
        self.__email = new_email

    def __str__(self):
        if self.email is None:
            return self.name
        elif self.name is None:
            return self.email
        else:
            return "%s (%s)" % (self.email, self.name)

    def __repr__(self):
        return "Person(name=%s, email=%s)" % (self.name, self.email)
