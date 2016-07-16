# -*- coding: utf-8 -*-
"""
    podgen.tests.test_media
    ~~~~~~~~~~~~~~~~~~~~~~~

    Test the Media class, which represents a pointer to a media file.

    :copyright: 2016, Thorben Dahl <thorben@sjostrom.no>
    :license: FreeBSD and LGPL, see license.* for more details.
"""
import os
import tempfile

from future.utils import iteritems
import unittest
import warnings
from datetime import timedelta
import mock
import io

from podgen import Media, NotSupportedByItunesWarning


class TestMedia(unittest.TestCase):
    def setUp(self):
        self.url = "http://example.com/2016/5/17/The+awesome+episode.mp3"
        self.size = 144253424
        self.type = "audio/mpeg"
        self.expected_type = ("audio/mpeg3", "audio/x-mpeg-3", "audio/mpeg")
        self.duration = timedelta(hours=1, minutes=32, seconds=44)
        warnings.simplefilter("always")
        def noop(*args, **kwargs):
            pass
        warnings.showwarning = noop

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
            '.mp3': set(["audio/mpeg"]),
            '.m4a': set(["audio/x-m4a"]),
            '.mov': set(["video/quicktime"]),
            '.mp4': set(["video/mp4"]),
            '.m4v': set(["video/x-m4v"]),
            '.pdf': set(["application/pdf"]),
            '.epub': set(["document/x-epub"]),
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

    @mock.patch("os.remove", autospec=True)
    @mock.patch("podgen.media.tempfile.NamedTemporaryFile", autospec=True)
    @mock.patch("podgen.media.TinyTag", autospec=True)
    def test_getDuration(self, mock_tinytag, mock_open, mock_rm):
        # Create our fake requests module
        mock_requests = mock.Mock()
        # Prepare the response which the code will get from requests.get()
        mock_requests_response = mock.Mock()
        # The content (supposed to be binary mp3 file)
        mock_requests_response.content = "binary data here"
        # The content, as returned by an iterator (supposed to be chunks of
        # mp3-file)
        mock_requests_response.iter_content.return_value = range(5)
        # Make sure our fake response is returned by requests.get()
        mock_requests.get.return_value = mock_requests_response

        # Return the correct number of seconds from TinyTag
        seconds = 14 * 60
        mock_tinytag.get.return_value.duration = seconds

        # Now do the actual testing
        m = Media(self.url, self.size, self.type)
        m.fetch_duration(mock_requests)
        self.assertAlmostEqual(m.duration.total_seconds(),
                               seconds, places=0)

        # Check that the underlying libraries were used correctly
        self.assertEqual(mock_requests.get.call_args[0][0], self.url)
        if 'stream' in mock_requests.get.call_args[1] and \
                mock_requests.get.call_args[1]['stream']:
            # The request is streamed, so iter_content was used
            mock_requests_response.iter_content.assert_called_once()
            fd = mock_open.return_value.__enter__.return_value
            expected = [((i,),) for i in range(5)]
            self.assertEqual(fd.write.call_args_list, expected)
        else:
            # The entire file was downloaded in one go
            mock_open.return_value.__enter__.return_value.\
                write.assert_called_once_with("binary data here")
        mock_rm.assert_called_once_with(mock_open.return_value.
                                        __enter__.return_value.name)

    def test_downloadMedia(self):
        class MyLittleRequests(object):
            @staticmethod
            def get(*args, **kwargs):
                self.assertEqual(args[0], self.url)
                is_streaming = kwargs.get("stream")

                class MyLittleResponse(object):
                    if is_streaming:
                        content = "binary content".encode("UTF-8")

                    @staticmethod
                    def iter_content(chunk_size):
                        assert chunk_size is None or chunk_size >= 1024
                        for char in "binary content":
                            yield char.encode("UTF-8")

                    @staticmethod
                    def raise_for_status():
                        pass

                return MyLittleResponse

        # Test that the given file object is used
        m = Media(self.url, self.size, self.type)
        fd = io.BytesIO()
        m.download(MyLittleRequests, fd)
        self.assertEqual(fd.getvalue().decode("UTF-8"), "binary content")
        fd.close()

        # Test that the given filename is used
        with tempfile.NamedTemporaryFile(delete=False) as fd:
            filename = fd.name
        try:
            m.download(MyLittleRequests, filename)
            with open(filename, "rb") as fd:
                self.assertEqual(fd.read().decode("UTF-8"), "binary content")
        finally:
            os.remove(filename)

    @mock.patch("podgen.media.TinyTag", autospec=True)
    def test_calculateDuration(self, mock_tinytag):
        # Return the correct number of seconds from TinyTag
        seconds = 14.0 * 60.0
        mock_tinytag.get.return_value.duration = seconds

        filename = "my_little_file.mp3"
        m = Media(self.url, self.size, self.type)
        m.populate_duration_from(filename)
        self.assertAlmostEqual(m.duration.total_seconds(), seconds, places=0)
        # Check that the underlying library is used correctly
        mock_tinytag.get.assert_called_once_with(filename)


