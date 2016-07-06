# -*- coding: utf-8 -*-
"""
    podgen.util
    ~~~~~~~~~~~~

    This file contains helper functions for the feed generator module.

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>
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
    """Make sure the locale setting do not interfere with the time format.
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
        return cgi.escape(s, quote=True)
else:
    import html

    def htmlencode(s):
        return html.escape(s)

def listToHumanreadableStr(l):
    # TODO: Allow translations of "and" and "empty"
    length = len(l)
    l = [str(e) for e in l]

    if length == 0:
        return "(empty)"
    elif length == 1:
        return l[0]
    else:
        return ", ".join(l[:-1]) + " and " + l[-1]
