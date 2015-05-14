"""Common test lib."""
import textwrap
import sys
from contextlib import contextmanager

PY2 = sys.version_info >= (2, 0) and sys.version_info < (3, 0)
PY3 = sys.version_info >= (3, 0) and sys.version_info < (4, 0)

if PY3:
    from io import StringIO
else:
    from StringIO import StringIO


@contextmanager
def capture(command, *args, **kwargs):
    """
    Capture the stdout temporarily in test environment.

    Takes a command to execute, and during its execution,
    we will redirect stdout so we can capture it.
    """

    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


def dedent(text):
    """De-indent strings."""

    return textwrap.dedent(text).strip()
