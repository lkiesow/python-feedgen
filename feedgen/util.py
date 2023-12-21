# -*- coding: utf-8 -*-
'''
    feedgen.util
    ~~~~~~~~~~~~

    This file contains helper functions for the feed generator module.

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>
    :license: FreeBSD and LGPL, see license.* for more details.
'''
import locale
import sys
import lxml  # nosec - we configure a safe parser below

# Configure a safe parser which does not allow XML entity expansion
parser = lxml.etree.XMLParser(
        attribute_defaults=False,
        dtd_validation=False,
        load_dtd=False,
        no_network=True,
        recover=False,
        remove_pis=True,
        resolve_entities=False,
        huge_tree=False)


def xml_fromstring(xmlstring):
    return lxml.etree.fromstring(xmlstring, parser)  # nosec - safe parser


def xml_elem(name, parent=None, **kwargs):
    if parent is not None:
        return lxml.etree.SubElement(parent, name, **kwargs)
    return lxml.etree.Element(name, **kwargs)


def ensure_format(val, allowed, required, allowed_values=None, defaults=None):
    '''Takes a dictionary or a list of dictionaries and check if all keys are
    in the set of allowed keys, if all required keys are present and if the
    values of a specific key are ok.

    :param val:            Dictionaries to check.
    :param allowed:        Set of allowed keys.
    :param required:       Set of required keys.
    :param allowed_values: Dictionary with keys and sets of their allowed
                           values.
    :param defaults:       Dictionary with default values.
    :returns:              List of checked dictionaries.
    '''
    if not val:
        return []
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

        for k, v in items:
            elem[k] = elem.get(k, v)
        if not set(elem.keys()) <= allowed:
            raise ValueError('Data contains invalid keys')
        if not set(elem.keys()) >= required:
            raise ValueError('Data contains not all required keys')

        if version == 2:
            values = allowed_values.iteritems()
        else:
            values = allowed_values.items()

        for k, v in values:
            if elem.get(k) and not elem[k] in v:
                raise ValueError('Invalid value for %s' % k)
    return val


def formatRFC2822(date):
    '''Make sure the locale setting do not interfere with the time format.
    '''
    old = locale.setlocale(locale.LC_ALL)
    locale.setlocale(locale.LC_ALL, 'C')
    date = date.strftime('%a, %d %b %Y %H:%M:%S %z')
    locale.setlocale(locale.LC_ALL, old)
    return date
