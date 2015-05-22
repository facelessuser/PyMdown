"""Common test lib."""
import textwrap
import sys
from contextlib import contextmanager
from pymdown import compat


@contextmanager
def capture(command, *args, **kwargs):
    """
    Capture the stdout temporarily in test environment.

    Takes a command to execute, and during its execution,
    we will redirect stdout so we can capture it.
    """

    out, sys.stdout = sys.stdout, compat.StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


def dedent(text):
    """De-indent strings."""

    return textwrap.dedent(text).strip()
