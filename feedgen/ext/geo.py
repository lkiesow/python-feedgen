from lxml import etree
from feedgen.ext.base import BaseExtension

class GeoExtension(BaseExtension):
    def __init__(self):
        self.__point__ = None

    def extend_ns(self):
        return { 'georss' : 'http://www.georss.org/georss' }

    def extend_rss(self, rss_feed):
        return rss_feed

    def extend_atom(self, atom_feed):
        return atom_feed
