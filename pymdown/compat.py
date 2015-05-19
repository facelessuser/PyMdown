"""
Module to provide compatibility between Py2 and Py3.

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
import sys
NOSETESTS = sys.argv[0].endswith('nosetests')

PY2 = sys.version_info >= (2, 0) and sys.version_info < (3, 0)
PY3 = sys.version_info >= (3, 0) and sys.version_info < (4, 0)

if sys.platform.startswith('win'):  # pragma: no cover
    PLATFORM = "windows"
elif sys.platform == "darwin":  # pragma: no cover
    PLATFORM = "osx"
else:  # pragma: no cover
    PLATFORM = "linux"

if PY3:  # pragma: no cover
    from urllib.parse import quote  # noqa
    from urllib.request import pathname2url  # noqa
    unicode_string = str
    string_type = str
    byte_string = bytes

    def stdout_write(text, encoding):
        """Write to stdout."""

        if not NOSETESTS:
            sys.stdout.buffer.write(text)
        else:
            sys.stdout.write(text.decode(encoding))

else:  # pragma: no cover
    from urllib import quote  # noqa
    from urllib import pathname2url  # noqa
    unicode_string = unicode  # noqa
    string_type = basestring  # noqa
    byte_string = str

    def stdout_write(text, encoding):
        """Write to stdout."""

        if not NOSETESTS:
            sys.stdout.write(text)
        else:
            sys.stdout.write(text.decode(encoding))


def print_stdout(text, encoding='utf-8'):
    """
    Write text out as bytes where possible.

    If someone overrides stdout, this may prove difficult.
    Nose for instance, will overrite stdout to capture it.
    This can be disabled by usint "nosetests -s", but it is also
    useful to allow nose to do this.  So we take the encoding
    and during "nosetests" we just convert it back to unicode
    as we will only work with stdout internally.
    """

    stdout_write(text, encoding)


def to_unicode(string, encoding='utf-8'):
    """Convert byte string to unicode."""

    return string.decode(encoding) if isinstance(string, byte_string) else string
