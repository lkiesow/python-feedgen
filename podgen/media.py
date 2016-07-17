# -*- coding: utf-8 -*-
"""
    podgen.media
    ~~~~~~~~~~~~

    This file contains the Media class, which represents a pointer to a media
    file.

    :copyright: 2016, Thorben Dahl <thorben@sjostrom.no>
    :license: FreeBSD and LGPL, see license.* for more details.
"""
import os
import tempfile
import warnings
from future.moves.urllib.parse import urlparse
from future.utils import raise_from
import datetime

from tinytag import TinyTag
import requests

from podgen.not_supported_by_itunes_warning import NotSupportedByItunesWarning
from podgen import version


def _get_new_requests_session():
    # TODO: Change into condition about requests' version once bug is fixed
    if False:
        requests_session = requests.Session()
        requests_session.headers['User-Agent'] = "%s v%s" % \
                                                 (version.name, version.version_full_str)
    else:
        # Currently work-around for bug in requests
        # See #3421 (https://github.com/kennethreitz/requests/issues/3421)
        requests_session = requests
    return requests_session


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

    .. seealso::
       :ref:`podgen.Media-guide`
          for a more gentle introduction.
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

    def __init__(self, url, size=0, type=None, duration=None,
                 requests_session=None):
        self._url = None
        self._size = None
        self._type = None
        self._duration = None

        self.url = url
        self.size = size
        self.type = type or self.get_type(url)
        self.duration = duration
        self.requests_session = requests_session or _get_new_requests_session()
        """The requests.Session object which shall be used. Defaults to a new
        session with PodGen as User-Agent.

        This is used by the instance methods :meth:`~.Media.download` and
        :meth:`~.Media.fetch_duration`.
        :meth:`~.Media.create_from_server_response`, however, creates its own
        requests Session if not given as a parameter (since it is a static
        method).

        You can set this attribute manually to set your own User-Agent and
        benefit from Keep-Alive across different instances of Media.

        :type: :class:`requests.Session`
        """

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
                          % file_extension, NotSupportedByItunesWarning,
                          stacklevel=2)
        if parsed_url.scheme not in ("http", "https"):
            warnings.warn("URL scheme %s is not supported by iTunes. Make sure "
                          "you use absolute URLs and HTTP or HTTPS."
                          % parsed_url.scheme, NotSupportedByItunesWarning,
                          stacklevel=2)
        self._url = url

    @property
    def file_extension(self):
        """The file extension of :attr:`~.Media.url`. Read-only.

        :type: :obj:`str`
        """
        return '.' + urlparse(self.url).path.split('.')[-1]

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
        """Parse ``size`` and return the number of bytes it names.
        See :attr:`.Media.size` for more information on this conversion."""
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
            warnings.warn("Media type %s is not supported by iTunes." % type,
                          NotSupportedByItunesWarning, stacklevel=2)
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
        file_extension = urlparse(url).path.split(".")[-1].lower()
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
    def create_from_server_response(cls, url, size=None, type=None,
                                    duration=None, requests_=None):
        """Create new Media object, with size and/or type fetched from the
        server when not given.

        See :meth:`.Media.fetch_duration` for a (slow!) way to fill in the
        duration as well.

        Example (assuming the server responds with Content-Length: 252345991 and
        Content-Type: audio/mpeg)::

            >>> from podgen import Media
            >>> # Assume an episode is hosted at example.com
            >>> m = Media.create_from_server_response(
            ...     "http://example.com/episodes/ep1.mp3")
            >>> m
            Media(url=http://example.com/episodes/ep1.mp3, size=252345991,
                type=audio/mpeg, duration=None)


        :param url: The URL at which the media can be accessed right now.
        :type url: str
        :param size: Size of the file. Will be fetched from server if not given.
        :type size: int or None
        :param type: The media type of the file. Will be fetched from server if
            not given.
        :type type: str or None
        :param duration: The media's duration.
        :type duration: :class:`datetime.timedelta` or :obj:`None`
        :param requests_: Either the
            `requests <http://docs.python-requests.org/en/master/>`_ module
            itself, or a :class:`requests.Session` object. Defaults to a new
            :class:`~requests.Session`.
        :type requests_: :mod:`requests` or :class:`requests.Session`
        :returns: New instance of Media with url, size and type filled in.
        :raises: The appropriate requests exceptions are thrown when networking
            errors occur. RuntimeError is thrown if some information isn't
            given and isn't found in the server's response."""
        if not (size and type):
            requests_ = requests_ or _get_new_requests_session()
            r = requests_.head(url, allow_redirects=True, timeout=10.0)
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

    def download(self, destination):
        """Download the media file.

        This method will block until the file is downloaded in its entirety.

        .. note::

            The destination will not be populated atomically; if you need this,
            you must give provide a temporary file as destination and rename the
            file yourself.

        :param destination: Where to save the media file. Either a filename,
            or a file-like object. The file-like object will *not* be closed by
            PodGen.
        :type destination: :obj:`fd` or :obj:`str`.
        """

        r = self.requests_session.get(self.url, stream=True)
        r.raise_for_status()
        fd = None
        destination_is_fd = hasattr(destination, "write")
        try:
            if destination_is_fd:
                fd = destination
            else:
                fd = open(destination, "wb")
            for chunk in r.iter_content(chunk_size=None):
                fd.write(chunk)
                del chunk
        except (Exception, KeyboardInterrupt, InterruptedError):
            # Don't leave half-finished files laying around.
            if fd and not destination_is_fd:
                try:
                    fd.close()
                    os.remove(destination)
                except FileNotFoundError:
                    pass
            raise
        finally:
            if fd and not destination_is_fd:
                # Close the file we've opened (doesn't hurt to close twice)
                fd.close()

    def populate_duration_from(self, filename):
        """Populate :attr:`.Media.duration` by analyzing the given file.

        Use this method when you have the media file on the local file system.
        Use :meth:`.Media.fetch_duration` if you need to download the file from
        the server.

        :param filename: Path to the media file which shall be used to determine
            this media's duration. The file extension must match its file type,
            since it is used to determine what type of media file it is. For
            a list of supported formats, see
            https://pypi.python.org/pypi/tinytag/
        :type filename: str
        """
        self.duration = self._get_duration_of(filename)

    @staticmethod
    def _get_duration_of(filename):
        """Return the duration of the media file located at ``filename``.

        Use :meth:`.Media.populate_duration_from` if you want to populate the
        duration property of a Media instance using a local file.

        :param filename: Path to the media file which shall be used to determine
            this media's duration. The file extension must match its file type,
            since it is used to determine what type of media file it is. For
            a list of supported formats, see
            https://pypi.python.org/pypi/tinytag/
        :type filename: str
        :returns: datetime.timedelta
        """
        return datetime.timedelta(seconds=TinyTag.get(filename).duration)

    def fetch_duration(self):
        """Download :attr:`.Media.url` locally and use it to populate
        :attr:`.Media.duration`.

        Use this method when you don't have the media file on the local file
        system. Use :meth:`~.Media.populate_duration_from` otherwise.

        This method will take quite some time, since the media file must be
        downloaded before it can be analyzed.
        """
        filename = None
        try:
            with tempfile.NamedTemporaryFile(
                    delete=False, suffix=self.file_extension) as fd:
                filename = fd.name
                self.download(fd)
            self.populate_duration_from(filename)
        finally:
            if filename:
                os.remove(filename)
