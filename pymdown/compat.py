"""
Module to provide compatibility between Py2 and Py3.

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
import sys

PY2 = sys.version_info >= (2, 0) and sys.version_info < (3, 0)
PY3 = sys.version_info >= (3, 0) and sys.version_info < (4, 0)

if PY2:
    from urllib import quote  # noqa
    from urllib import pathname2url  # noqa
    from StringIO import StringIO  # noqa
    unicode_type = unicode  # noqa
    string_type = basestring  # noqa
    binary_type = str
else:
    from urllib.parse import quote  # noqa
    from urllib.request import pathname2url  # noqa
    from io import StringIO  # noqa
    unicode_type = str  # noqa
    string_type = str  # noqa
    binary_type = bytes  # noqa

NOSETESTS = sys.argv[0].endswith('nosetests')

if sys.platform.startswith('win'):  # pragma: no cover
    PLATFORM = "windows"
elif sys.platform == "darwin":  # pragma: no cover
    PLATFORM = "osx"
else:  # pragma: no cover
    PLATFORM = "linux"


def print_stdout(text, encoding='utf-8'):
    """
    Write text out as bytes where possible.

    If someone overrides stdout, this may prove difficult.
    Nose for instance, will overrite stdout to capture it.
    This can be disabled by using "nosetests -s", but it is also
    useful to allow nose to do this.  So we take the encoding
    and during "nosetests" we just convert it back to unicode
    as we will only work with stdout internally.
    """

    if PY3:
        if not NOSETESTS:  # pragma: no cover
            sys.stdout.buffer.write(text)
        else:
            sys.stdout.write(text.decode(encoding))
    else:
        if not NOSETESTS:  # pragma: no cover
            sys.stdout.write(text)
        else:
            sys.stdout.write(text.decode(encoding))


def to_unicode(string, encoding='utf-8'):
    """Convert byte string to unicode."""

    return unicode_type(string, encoding) if isinstance(string, binary_type) else string
