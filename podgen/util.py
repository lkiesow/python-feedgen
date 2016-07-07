# -*- coding: utf-8 -*-
"""
    podgen.util
    ~~~~~~~~~~~~

    This file contains helper functions for the feed generator module.

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de> and 2016, Thorben Dahl
        <thorben@sjostrom.no>
    :license: FreeBSD and LGPL, see license.* for more details.
"""
import sys, locale


def ensure_format(val, allowed, required, allowed_values=None, defaults=None):
    """Takes a dictionary or a list of dictionaries and check if all keys are in
    the set of allowed keys, if all required keys are present and if the values
    of a specific key are ok.

    :param val:            Dictionaries to check.
    :param allowed:        Set of allowed keys.
    :param required:       Set of required keys.
    :param allowed_values: Dictionary with keys and sets of their allowed values.
    :param defaults:       Dictionary with default values.
    :returns:              List of checked dictionaries.
    """
    # TODO: Check if this function is obsolete and perhaps remove it
    if not val:
        return None
    if allowed_values is None:
        allowed_values = {}
    if defaults is None:
        defaults = {}
    # Make shure that we have a list of dicts. Even if there is only one.
    if not isinstance(val, list):
        val = [val]
    for elem in val:
        if not isinstance(elem, dict):
            raise ValueError('Invalid data (value is no dictionary)')
        # Set default values

        version = sys.version_info[0]

        if version == 2:
            items = defaults.iteritems()
        else:
            items = defaults.items()

        for k,v in items:
            elem[k] = elem.get(k, v)
        if not set(elem.keys()) <= allowed:
            raise ValueError('Data contains invalid keys')
        if not set(elem.keys()) >= required:
            raise ValueError('Data contains not all required keys')

        if version == 2:
            values = allowed_values.iteritems()
        else:
            values = allowed_values.items()

        for k,v in values:
            if elem.get(k) and not elem[k] in v:
                raise ValueError('Invalid value for %s' % k )
    return val


def formatRFC2822(d):
    """Format a datetime according to RFC2822.

    This implementation exists as a workaround to ensure that the locale setting
    does not interfere with the time format. For example, day names might get
    translated to your local language, which would break with the standard.

    :param d: Time and date you want to format according to RFC2822.
    :type d: datetime.datetime
    :returns: The datetime formatted according to the RFC2822.
    :rtype: str
    """
    l = locale.setlocale(locale.LC_ALL)
    locale.setlocale(locale.LC_ALL, 'C')
    d = d.strftime('%a, %d %b %Y %H:%M:%S %z')
    locale.setlocale(locale.LC_ALL, l)
    return d

# Define htmlencode
ver = sys.version_info

if ver < (3, 2):
    # cgi.escape was deprecated in 3.2
    import cgi

    def htmlencode(s):
        """Encode the given string so its content won't be confused as HTML
        markup.

        This function exists as a cross-version compatibility alias."""
        return cgi.escape(s, quote=True)
else:
    import html

    def htmlencode(s):
        """Encode the given string so its content won't be confused as HTML
        markup.

        This function exists as a cross-version compatibility alias."""
        return html.escape(s)


def listToHumanreadableStr(l):
    """Create a human-readable string out of the given iterable.

    Example::

        >>> from podgen.util import listToHumanreadableStr
        >>> listToHumanreadableStr([1, 2, 3])
        1, 2 and 3

    The string ``(empty)`` is returned if the list is empty – it is assumed
    that you check whether the list is empty yourself.
    """
    # TODO: Allow translations of "and" and "empty"
    length = len(l)
    l = [str(e) for e in l]

    if length == 0:
        return "(empty)"
    elif length == 1:
        return l[0]
    else:
        return ", ".join(l[:-1]) + " and " + l[-1]
