from lxml import etree
from feedgen.ext.base import BaseEntryExtension

class GeoEntryExtension(BaseEntryExtension):
    def __init__(self):
        self.__point = None

    def extend_rss(self, entry):
        GEO_NS = 'http://www.georss.org/georss'

        if self.__point:
            point = etree.SubElement(entry, '{%s}point' % GEO_NS)
            point.text = self.__point

        return entry

    def extend_atom(self, entry):
        return self.extend_rss(self, entry)

    def point(self, point=None):
        self.__point = point or '0.0 0.0'
        return self.__point
