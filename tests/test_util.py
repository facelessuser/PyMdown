import unittest
from collections import OrderedDict
from pymdown import util
from . import common
import os


class TestFrontmatter(unittest.TestCase):
    def test_yaml_load(self):
        yaml_text = common.dedent('''
            test:
                key1: 1
                key2: 2
                key3: 3
                key4: 4
                key5: 5
                key5: 6
                key3: 7
        ''')

        self.assertEqual(
            util.yaml_load(yaml_text),
            OrderedDict([('test', OrderedDict([('key1', 1), ('key2', 2),
                                               ('key3', 7), ('key4', 4),
                                               ('key5', 6)]))])
        )

    def test_whatever(self):
        pass


class TestResources(unittest.TestCase):
    def test_text_resource(self):
        text1 = util.load_text_resource(
            os.path.join('pymdown', 'data', 'licenses.txt')
        )

        text2 = util.load_text_resource(
            os.path.join('pymdown', 'data', 'licenses.txt'),
            internal=True
        )

        with open(os.path.join('pymdown', 'data', 'licenses.txt'), 'rb') as f:
            text3 = f.read()

        text4 = util.load_text_resource(
            os.path.join('pymdown', 'data', 'not-exist.txt')
        )

        self.assertEqual(text1, text3)
        self.assertEqual(text2, text3)
        self.assertEqual(None, text4)
