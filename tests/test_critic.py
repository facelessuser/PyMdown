from __future__ import unicode_literals
import unittest
from . import common
from pymdown import critic_dump


class TestCritic(unittest.TestCase):
    text = common.dedent(
        '''
        # This is a {~~test~>Unit Test~~}
        This is a {++CritcMarkup ++}{--test to --}test{-- CriticMarkup--}.

        {==This is a good test.==}{>>This probably isn't needed.<<}
        '''
    )

    def test_accept(self):
        cd = critic_dump.CriticDump()
        result = cd.dump(self.text, True)

        expected = common.dedent(
            '''
            # This is a Unit Test
            This is a CritcMarkup test.

            This is a good test.
            '''
        )

        self.assertEqual(result, expected)

    def test_reject(self):
        cd = critic_dump.CriticDump()
        result = cd.dump(self.text, False)

        expected = common.dedent(
            '''
            # This is a test
            This is a test to test CriticMarkup.

            This is a good test.
            '''
        )

        self.assertEqual(result, expected)

    def test_view(self):
        cd = critic_dump.CriticDump()
        result = cd.dump(self.text, False, True)

        expected = common.dedent(
            '''
            # This is a <del class="critic">test</del><ins class="critic">Unit Test</ins>
            This is a <ins class="critic">CritcMarkup </ins><del class="critic">test to </del>test<del class="critic"> CriticMarkup</del>.

            <mark class="critic">This is a good test.</mark><span class="critic comment">This probably isn't needed.</span>
            '''  # noqa
        )

        self.assertEqual(result, expected)
