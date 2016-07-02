import warnings
from future.moves.urllib.parse import urlparse

from feedgen.not_supported_by_itunes_warning import NotSupportedByItunesWarning


class Media(object):
    """
    Data-oriented class representing a pointer to a media file.

    A media file can be a sound file (most typical), video file or a document.

    You should provide the url at which this media can be found, and the media's
    file size in bytes. Optionally, you can provide the type of media
    (expressed in the media type format). When not given in the constructor, it
    will be found automatically by looking at the url's file extension. If the
    url's file extension isn't supported by iTunes, you will get an error if you
    don't supply the type.

    .. note::

        iTunes is lazy and will just look at the URL to figure out if
        a file is of a supported file type. You must therefore ensure your URL
        ends with a supported file extension.

    .. note::

        A warning called :class:`~feedgen.not_supported_by_itunes_warning.NotSupportedByItunesWarning`
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

    def __init__(self, url, size=0, type=None):
        self._url = None
        self._size = None
        self._type = None

        self.url = url
        self.size = size
        self.type = type or self.get_type(url)

    @property
    def url(self):
        """The URL at which this media is publicly accessible.

        Only absolute URLs are allowed, so make sure it starts with http:// or
        https://. The server should support HEAD-requests in addition to
        multi-range requests."""
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

        You can either provide the number of bytes as an int, or you can
        provide a human-readable str with a unit, like MB or GiB.

        An unknown size is represented as 0. You should strive to provide a
        size, so your listeners aren't surprised by any big files.

        .. note::

            If you provide a string, it will be translated to int when the
            assignment happens. Thus, on subsequent access, you will get the
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
        """The media type of this media.

        See https://en.wikipedia.org/wiki/Media_type for an introduction.

        .. note::

            If you leave out type when creating a new Media object, the
            type will be auto-detected from the :attr:`~feedgen.media.Media.url`
            attribute. However, this won't happen automatically other than
            during initialization. If you want to autodetect type when
            assigning a new value to url, you should use
            :meth:`~feedgen.media.Media.get_type`.
        """
        return self._type

    @type.setter
    def type(self, type):
        type = type.strip().lower()

        if not type in self.file_types.values():
            warnings.warn("Media type %s is not supported by iTunes.",
                          NotSupportedByItunesWarning)
        self._type = type

    def get_type(self, url):
        """Autodetect the media type, given the url.

        Example::

            >>> from feedgen.media import Media
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
        """
        file_extension = urlparse(url).path.split(".")[-1]
        try:
            return self.file_types[file_extension]
        except KeyError as e:
            raise ValueError("The file extension %s was not recognized, which "
                             "means it's not supported by iTunes. If this is "
                             "intended, please provide the type yourself so "
                             "clients can see what type of file it is."
                             % file_extension) from e



