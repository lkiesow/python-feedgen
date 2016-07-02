from future.utils import iteritems
import unittest
import warnings

from feedgen.media import Media
from feedgen.not_supported_by_itunes_warning import NotSupportedByItunesWarning

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.url = "http://example.com/2016/5/17/The+awesome+episode.mp3"
        self.size = 144253424
        self.type = "audio/mpeg"
        self.expected_type = ("audio/mpeg3", "audio/x-mpeg-3", "audio/mpeg")
        warnings.simplefilter("ignore")

    def test_constructorOneArgument(self):
        m = Media(self.url)
        assert m.url == self.url
        assert m.size == 0
        assert m.type in self.expected_type

    def test_constructorTwoArguments(self):
        m = Media(self.url, self.size)
        assert m.url == self.url
        assert m.size == self.size
        assert m.type in self.expected_type

    def test_constructorThreeArguments(self):
        m = Media(self.url, self.size, self.type)
        assert m.url == self.url
        assert m.size == self.size
        assert m.type == self.type

    def test_assigningUrl(self):
        m = Media(self.url)
        another_url = "http://example.com/2016/5/17/The+awful+episode.mp3"
        m.url = another_url
        assert m.url == another_url

    def test_assigningSize(self):
        m = Media(self.url, self.size)
        another_size = 1234567
        m.size = another_size
        assert m.size == another_size

    def test_assigningType(self):
        m = Media(self.url, self.size, self.type)
        another_type = "audio/x-mpeg-3"
        m.type = another_type
        assert m.type == another_type

    def test_autoRecognizeType(self):
        url = "http://example.com/2016/5/17/The+converted+episode%s"

        # Mapping between url file extension and type given by iTunes
        # https://help.apple.com/itc/podcasts_connect/#/itcb54353390
        types = {
            '.mp3': {"audio/mpeg"},
            '.m4a': {"audio/x-m4a"},
            '.mov': {"video/quicktime"},
            '.mp4': {"video/mp4"},
            '.m4v': {"video/x-m4v"},
            '.pdf': {"application/pdf"},
            '.epub': {"document/x-epub"},
        }

        for (file_extension, allowed_types) in iteritems(types):
            m = Media(url % file_extension)
            assert m.type in allowed_types, "%s gave type %s, expected %s" % \
                                            (file_extension, m.type,
                                             allowed_types)

    def test_invalidFileExtension(self):
        self.assertRaises(ValueError, Media, "http://episode.example.org/1")
        self.assertRaises(ValueError, Media, "http://ep.example.org/.mp3/1.mp2")

    def test_anyExtensionAllowedWithType(self):
        m = Media("http://episode.example.org/yo.ogg",
                  3453245,
                  "audio/ogg")

    def test_warningGivenIfNotSupportedByItunes(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(len(w), 0)
            # Use a type not supported by itunes
            self.test_anyExtensionAllowedWithType()
            # Check that two warnings were issued
            self.assertEqual(len(w), 2)
            # Warning: file extension not recognized
            assert issubclass(w[0].category, NotSupportedByItunesWarning), \
                str(w[0])
            # Warning: type not recognized
            assert issubclass(w[1].category, NotSupportedByItunesWarning)

            # Use url extension supported by itunes, but a type not supported
            m = Media(self.url, self.size, "audio/mpeg3")
            # Check that a new warning was issued
            assert len(w) == 3
            # Warning: type not recognized
            assert issubclass(w[2].category, NotSupportedByItunesWarning)

    def test_strToSize(self):
        sizes = {
            "12 kB": 12000,
            "12 kib": 12288,
            "15MB": 15000000,
            "15MiB": 15728640,
            "0.32GB": 320000000,
            "0.32GiB": 343597384,
            "462GB": 462000000000,
            "4TB": 4000000000000,
            "4 TiB": 4398046511104,
            "1 000 KB": 1000000,
            "145B": 145,
        }

        for (str_size, expected_size) in iteritems(sizes):
            self.assertEqual(expected_size, Media._str_to_bytes(str_size))
