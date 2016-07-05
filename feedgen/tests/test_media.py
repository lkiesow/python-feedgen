from future.utils import iteritems
import unittest
import warnings
from datetime import timedelta

from feedgen import Media, NotSupportedByItunesWarning


class TestMedia(unittest.TestCase):
    def setUp(self):
        self.url = "http://example.com/2016/5/17/The+awesome+episode.mp3"
        self.size = 144253424
        self.type = "audio/mpeg"
        self.expected_type = ("audio/mpeg3", "audio/x-mpeg-3", "audio/mpeg")
        self.duration = timedelta(hours=1, minutes=32, seconds=44)
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

    def test_constructorDuration(self):
        m = Media(self.url, self.size, self.type, self.duration)
        assert m.duration ==self.duration

    def test_assigningUrl(self):
        m = Media(self.url)
        another_url = "http://example.com/2016/5/17/The+awful+episode.mp3"
        m.url = another_url
        assert m.url == another_url
        # Test that setting url to None or empty string fails
        self.assertRaises((ValueError, TypeError), setattr, m, "url", None)
        assert m.url == another_url
        self.assertRaises((ValueError, TypeError), setattr, m, "url", "")
        assert m.url == another_url

    def test_assigningSize(self):
        m = Media(self.url, self.size)
        another_size = 1234567
        m.size = another_size
        assert m.size == another_size

    def test_warningWhenSettingSizeToZero(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(len(w), 0)

            # Set size to zero, triggering a warning
            m = Media(self.url, type=self.type)
            self.assertEqual(len(w), 1)
            assert issubclass(w[-1].category, UserWarning)

            # No warning when setting to an actual integer
            m.size = 253634535
            self.assertEqual(len(w), 1)

            # Nor when using a string
            m.size = "15kB"
            self.assertEqual(len(w), 1)

            # Warning when setting to None
            m.size = None
            self.assertEqual(len(w), 2)
            assert issubclass(w[-1].category, UserWarning)

            # Or zero
            m.size = 0
            self.assertEqual(len(w), 3)
            assert issubclass(w[-1].category, UserWarning)

    def test_assigningType(self):
        m = Media(self.url, self.size, self.type)
        another_type = "audio/x-mpeg-3"
        m.type = another_type
        assert m.type == another_type
        # Test that setting type to None or empty string fails
        self.assertRaises((ValueError, TypeError), setattr, m, "type", None)
        assert m.type == another_type
        self.assertRaises((ValueError, TypeError), setattr, m, "type", "")
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

    def test_assigningDuration(self):
        m = Media(self.url, self.size, self.type, self.duration)
        another_duration = timedelta(hours=0, minutes=32, seconds=23)
        m.duration = another_duration
        self.assertEqual(m.duration, another_duration)

    def test_assigningNegativeDuration(self):
        self.assertRaises(ValueError, Media, self.url, self.size, self.type,
                          timedelta(hours=-1, minutes=3))

    def test_assigningNotDuration(self):
        self.assertRaises(TypeError, Media, self.url, self.size, self.type,
                          "01:32:13")

    def test_durationToStr(self):
        m = Media(self.url, self.size, self.type, timedelta(hours=1))
        self.assertEqual(m.duration_str, "01:00:00")

        m.duration = timedelta(days=1)
        self.assertEqual(m.duration_str, "24:00:00")

        m.duration = timedelta(minutes=1)
        self.assertEqual(m.duration_str, "01:00")

        m.duration = timedelta(seconds=1)
        self.assertEqual(m.duration_str, "00:01")

        m.duration = timedelta(days=1, hours=2)
        self.assertEqual(m.duration_str, "26:00:00")

        m.duration = timedelta(hours=1, minutes=32, seconds=13)
        self.assertEqual(m.duration_str, "01:32:13")

        m.duration = timedelta(hours=1, minutes=9, seconds=3)
        self.assertEqual(m.duration_str, "01:09:03")

    def test_createFromServerResponse(self):
        # Mock our own requests object
        url = self.url
        type = self.type
        size = self.size

        class MyLittleRequests(object):
            @staticmethod
            def head(*args, **kwargs):
                assert args[0] == url
                assert kwargs['allow_redirects'] == True
                assert 'timeout' in kwargs
                assert 'headers' in kwargs
                assert 'User-Agent' in kwargs['headers']

                class MyLittleResponse(object):
                    headers = {
                        'Content-Type': type,
                        'Content-Length': size,
                    }

                    @staticmethod
                    def raise_for_status():
                        pass

                return MyLittleResponse

        m = Media.create_from_server_response(MyLittleRequests, url,
                                              duration=self.duration)
        self.assertEqual(m.url, url)
        self.assertEqual(m.size, size)
        self.assertEqual(m.type, type)
        self.assertEqual(m.duration, self.duration)


