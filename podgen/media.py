# -*- coding: utf-8 -*-
"""
    podgen.media
    ~~~~~~~~~~~~

    This file contains the Media class, which represents a pointer to a media
    file.

    :copyright: 2016, Thorben Dahl <thorben@sjostrom.no>
    :license: FreeBSD and LGPL, see license.* for more details.
"""
import warnings
from future.moves.urllib.parse import urlparse
from future.utils import raise_from
import datetime

from podgen.not_supported_by_itunes_warning import NotSupportedByItunesWarning
from podgen import version


class Media(object):
    """
    Data-oriented class representing a pointer to a media file.

    A media file can be a sound file (most typical), video file or a document.

    You should provide the absolute URL at which this media can be found, and
    the media's file size in bytes.

    Optionally, you can provide the type of media (expressed using MIME types).
    When not given in the constructor, it will be found automatically by looking
    at the url's file extension. If the url's file extension isn't supported by
    iTunes, you will get an error if you don't supply the type.

    You are also highly encouraged to provide the duration of the media.

    .. note::

        iTunes is lazy and will just look at the URL to figure out if
        a file is of a supported file type. You must therefore ensure your URL
        ends with a supported file extension.

    .. note::

        A warning called :class:`~podgen.NotSupportedByItunesWarning`
        will be issued if your URL or type isn't compatible with iTunes. See
        the Python documentation for more details on :mod:`warnings`.

    Media types supported by iTunes:

    * Audio
      * M4A
      * MP3
    * Video
      * MOV
      * MP4
      * M4V
    * Document
      * PDF
      * EPUB

    All attributes will always have a value, except size which can be 0 if the
    size cannot be determined by any means (eg. if it's a stream) and duration
    which is optional (but recommended).


    """
    file_types = {
        'm4a': 'audio/x-m4a',
        'mp3': 'audio/mpeg',
        'mov': 'video/quicktime',
        'mp4': 'video/mp4',
        'm4v': 'video/x-m4v',
        'pdf': 'application/pdf',
        'epub': 'document/x-epub',
    }

    def __init__(self, url, size=0, type=None, duration=None):
        self._url = None
        self._size = None
        self._type = None
        self._duration = None

        self.url = url
        self.size = size
        self.type = type or self.get_type(url)
        self.duration = duration

    @property
    def url(self):
        """The URL at which this media is publicly accessible.

        Only absolute URLs are allowed, so make sure it starts with http:// or
        https://. The server should support HEAD-requests and byte-range
        requests.

        :type: :obj:`str`
        """
        return self._url

    @url.setter
    def url(self, url):
        if not url:
            raise ValueError("url cannot be empty or None")
        parsed_url = urlparse(url)
        file_extension = parsed_url.path.split('.')[-1].lower()
        if file_extension not in self.file_types:
            warnings.warn("File extension %s is not supported by iTunes."
                          % file_extension, NotSupportedByItunesWarning)
        if parsed_url.scheme not in ("http", "https"):
            warnings.warn("URL scheme %s is not supported by iTunes. Make sure "
                          "you use absolute URLs and HTTP or HTTPS."
                          % parsed_url.scheme, NotSupportedByItunesWarning)
        self._url = url

    @property
    def size(self):
        """The media's file size in bytes.

        You can either provide the number of bytes as an :obj:`int`, or you can
        provide a human-readable :obj:`str` with a unit, like MB or GiB.

        An unknown size is represented as 0. This should ONLY be used in
        exceptional cases, where it is theoretically impossible to determine
        the file size (for example if it's a stream). Setting the size to 0
        will issue a UserWarning.

        :type: :obj:`str` (which will be converted to and stored as :obj:`int`)
            or :obj:`int`

        .. note::

            If you provide a string, it will be translated to int when the
            assignment happens. Thus, on subsequent accesses, you will get the
            resulting int, not the string you put in.

        .. note::

            The units are case-insensitive. This means that the ``B`` is
            always assumed to mean "bytes", even if it is lowercase (``b``).
            Likewise, ``m`` is taken to mean mega, not milli.
        """
        return self._size

    @size.setter
    def size(self, size):
        try:
            size = int(size)
            if size < 0:
                raise ValueError("File size must be 0 if unknown, or a positive"
                                 " integer.")
            self._size = size
            if self.size == 0:
                warnings.warn("Size is set to 0. This should ONLY be done when "
                              "there is no possible way to determine the "
                              "media's size, like if the media is a stream.",
                              stacklevel=3)
        except ValueError:
            self.size = self._str_to_bytes(size)
        except TypeError as e:
            if size is None:
                self.size = 0
            else:
                raise e
    @staticmethod
    def _str_to_bytes(size):
            units = {
                "b": 1,
                "kb": 1000,
                "kib": 1024,
                "mb": 1000**2,
                "mib": 1024**2,
                "gb": 1000**3,
                "gib": 1024**3,
                "tb": 1000**4,
                "tib": 1024**4
            }
            size = str(size).lower().strip().replace(" ", "")
            number = float(size.rstrip("bkimgt"))
            unit = size.lstrip("0123456789.")
            try:
                return round(number * units[unit])
            except KeyError:
                raise ValueError("The unit %s was not recognized." % unit)

    @property
    def type(self):
        """The MIME type of this media.

        See https://en.wikipedia.org/wiki/Media_type for an introduction.

        :type: :obj:`str`

        .. note::

            If you leave out type when creating a new Media object, the
            type will be auto-detected from the :attr:`~podgen.Media.url`
            attribute. However, this won't happen automatically other than
            during initialization. If you want to autodetect type when
            assigning a new value to url, you should use
            :meth:`~podgen.Media.get_type`.
        """
        return self._type

    @type.setter
    def type(self, type):
        if not type:
            raise ValueError("Type cannot be empty or None")

        type = type.strip().lower()

        if type not in self.file_types.values():
            warnings.warn("Media type %s is not supported by iTunes.",
                          NotSupportedByItunesWarning)
        self._type = type

    def get_type(self, url):
        """Guess the MIME type from the URL.

        This is used to fill in :attr:`~.Media.type` when it is not given (and
        thus called implicitly by the constructor), but you can call it
        yourself.

        Example::

            >>> from podgen import Media
            >>> m = Media("http://example.org/1.mp3", 136532744)
            >>> # The type was detected from the url:
            >>> m.type
            audio/mpeg
            >>> # Ops, I changed my mind...
            >>> m.url = "https://example.org/1.m4a"
            >>> # As you can see, the type didn't change:
            >>> m.type
            audio/mpeg
            >>> # So update type yourself
            >>> m.type = m.get_type(m.url)
            >>> m.type
            audio/x-m4a

        :param url: The URL which should be used to guess the MIME type.
        :type url: str
        :returns: The guessed MIME type.
        :raises: ValueError if the MIME type couldn't be guessed from the URL.
        """
        file_extension = urlparse(url).path.split(".")[-1]
        try:
            return self.file_types[file_extension]
        except KeyError as e:
            raise_from(ValueError(
                "The file extension %s was not recognized, which means it's "
                "not supported by iTunes. If this is intended, please provide "
                "the type yourself so clients can see what type of file it is."
                % file_extension), e)

    @property
    def duration(self):
        """The duration of the media file.

        :type: :class:`datetime.timedelta`
        :raises: :obj:`TypeError` if you try to assign anything other than
            :class:`datetime.timedelta` or :obj:`None` to this attribute. Raises
            :obj:`ValueError` if a negative timedelta value is given.
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        if duration is None:
            self._duration = None
        elif not isinstance(duration, datetime.timedelta):
            raise TypeError("duration must be a datetime.timedelta instance!")
        elif duration.total_seconds() < 0:
            raise ValueError("expected a positive timedelta, got %s" % duration)
        else:
            self._duration = duration

    @property
    def duration_str(self):
        """:attr:`.duration`, formatted as a string according to iTunes' specs.
        That is, HH:MM:SS if it lasts more than an hour, or MM:SS if it lasts
        less than an hour.

        This is just an alternate, read-only view of :attr:`.duration`.

        If :attr:`.duration` is :obj:`None`, then this will be :obj:`None` as
        well.

        :type: :obj:`str`
        """
        if self.duration is None:
            return None
        else:
            hours = self.duration.days * 24 + \
                    self.duration.seconds // 3600
            minutes = (self.duration.seconds // 60) % 60
            seconds = self.duration.seconds % 60

            if hours:
                return "%02d:%02d:%02d" % (hours, minutes, seconds)
            else:
                return "%02d:%02d" % (minutes, seconds)

    @classmethod
    def create_from_server_response(cls, requests, url, size=None, type=None,
                                    duration=None):
        """Create new Media object, with size and/or type fetched from the
        server when not given.

        Like the signature suggests, this factory method requires that
        `Requests <http://docs.python-requests.org/en/master/>`_ is installed.

        Example (assuming the server responds with Content-Length: 252345991 and
        Content-Type: audio/mpeg)::

            >>> from podgen import Media
            >>> import requests  # from requests package
            >>> # Assume an episode is hosted at example.com
            >>> m = Media.create_from_server_response(requests,
            ...     "http://example.com/episodes/ep1.mp3")
            >>> m
            Media(url=http://example.com/episodes/ep1.mp3, size=252345991,
                type=audio/mpeg, duration=None)


        :param requests: Either the
            `requests <http://docs.python-requests.org/en/master/>`_ module
            itself, or a Session object.
        :type requests: requests
        :param url: The URL at which the media can be accessed right now.
        :type url: str
        :param size: Size of the file. Will be fetched from server if not given.
        :type size: int or None
        :param type: The media type of the file. Will be fetched from server if
            not given.
        :type type: str or None
        :param duration: The media's duration.
        :type duration: :class:`datetime.timedelta` or :obj:`None`.
        :returns: New instance of Media with url, size and type filled in.
        :raises: The appropriate requests exceptions are thrown when networking
            errors occur. RuntimeError is thrown if some information isn't
            given and isn't found in the server's response."""
        if not (size and type):
            r = requests.head(url, allow_redirects=True, timeout=5.0,
                              headers={"User-Agent": version.name + " v" +
                                                     version.version_full_str})
            r.raise_for_status()
            if not size:
                try:
                    size = r.headers['Content-Length']
                except KeyError:
                    raise RuntimeError("Content-Length not returned by server "
                                       "when sending HEAD request to %s" % url)
            if not type:
                try:
                    type = r.headers['Content-Type']
                except KeyError:
                    raise RuntimeError("Content-Type header not returned by "
                                       "server when sending HEAD request to %s"
                                       % url)

        return Media(url, size, type, duration)

    def __str__(self):
        return "Media(url=%s, size=%s, type=%s, duration=%s)" % \
               (self.url, self.size, self.type, self.duration)

    def __repr__(self):
        return self.__str__()
