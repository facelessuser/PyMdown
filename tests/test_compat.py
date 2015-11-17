# -*- coding: utf-8 -*-
"""Unit test for compatability lib."""
from __future__ import unicode_literals
import unittest
from pymdown import compat
from . import common


class TestCompat(unittest.TestCase):
    """TestCompat."""

    def test_unicode(self):
        """Test converting from bytes to unicode."""

        ustr = "Ā ā Ă ă Ą ą"
        bstr = ustr.encode('utf-8')
        ustr2 = compat.to_unicode(bstr, 'utf-8')
        self.assertEqual(ustr, ustr2)

    def test_output(self):
        """Test that we can dump to stdout properly."""

        ustr = "Ā ā Ă ă Ą ą"
        with common.capture(compat.print_stdout, ustr.encode('utf-8'), 'utf-8') as output:
            self.assertEqual(ustr, output)
