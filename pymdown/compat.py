import sys

PY2 = sys.version_info >= (2, 0) and sys.version_info < (3, 0)
PY3 = sys.version_info >= (3, 0) and sys.version_info < (4, 0)

if sys.platform.startswith('win'):
    PLATFORM = "windows"
elif sys.platform == "darwin":
    PLATFORM = "osx"
else:
    PLATFORM = "linux"

if PY3:
    from urllib.parse import quote
    from urllib.request import pathname2url
    unicode_string = str
    string_type = str
    byte_string = bytes
    stdout_write = sys.stdout.buffer.write
else:
    from urllib import quote  # noqa
    from urllib import pathname2url  # noqa
    unicode_string = unicode  # noqa
    string_type = basestring  # noqa
    byte_string = str
    stdout_write = sys.stdout.write


def to_unicode(string, encoding='utf-8'):
    """ Convert byte string to unicode """
    return string.decode(encoding) if isinstance(string, byte_string) else string
