from __future__ import unicode_literals
import unittest
from collections import OrderedDict
from pymdown import util
from pymdown import settings
import os


class TestSettings(unittest.TestCase):
    def test_critic_prevent_override(self):
        s = settings.Settings(
            critic=util.CRITIC_ACCEPT,
            settings_path=os.path.join('tests', 'settings', 'critic.cfg')
        )
        s.read_settings()
        new_s = s.get('Untitled')

        option = new_s.get('settings').get('extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'accept')

    def test_critic_allow_override(self):
        s = settings.Settings(
            settings_path=os.path.join('tests', 'settings', 'critic.cfg')
        )
        s.read_settings()
        new_s = s.get('Untitled')

        option = new_s.get('settings').get('extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'reject')

    def test_critic_frontmatter_override(self):
        s = settings.Settings(
            settings_path=os.path.join('tests', 'settings', 'critic.cfg')
        )
        s.read_settings()
        new_s = s.get(
            'Untitled',
            frontmatter=OrderedDict(
                [('settings', OrderedDict(
                    [('extensions', OrderedDict(
                        [('pymdownx.critic', OrderedDict(
                            [('mode', 'accept')]
                        ))]
                    ))]
                ))]
            )
        )

        option = new_s.get('settings').get('extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'accept')

    def test_plain_prevent_override(self):
        s = settings.Settings(
            plain=True,
            settings_path=os.path.join('tests', 'settings', 'plain.cfg')
        )
        s.read_settings()
        new_s = s.get('Untitled')

        options = new_s.get('settings').get('extensions').get('pymdownx.plainhtml')
        self.assertEqual(options, None)

    def test_plain_allow_override(self):
        s = settings.Settings(
            settings_path=os.path.join('tests', 'settings', 'plain.cfg')
        )
        s.read_settings()
        new_s = s.get('Untitled')

        option = new_s.get('settings').get('extensions').get('pymdownx.plainhtml').get('strip_comments', None)
        self.assertEqual(option, False)

    def test_pygments_no_style(self):
        s = settings.Settings(
            settings_path=os.path.join('tests', 'settings', 'pygments_no_style.cfg')
        )
        s.read_settings()
        new_s = s.get('Untitled')

        style = new_s.get('settings').get('style')
        self.assertEqual(style, 'default')
        pygments_css = new_s.get('settings').get('pygments_class')
        self.assertEqual(pygments_css, 'codehilite')

    def test_pygments_bad_style(self):
        s = settings.Settings(
            settings_path=os.path.join('tests', 'settings', 'pygments_bad_style.cfg')
        )
        s.read_settings()
        new_s = s.get('Untitled')

        style = new_s.get('settings').get('style')
        self.assertEqual(style, 'default')

    def test_no_pygments(self):
        s = settings.Settings(
            settings_path=os.path.join('tests', 'settings', 'no_pygments.cfg')
        )
        s.read_settings()
        new_s = s.get('Untitled')

        use_pygments_css = new_s.get('settings').get('use_pygments_css')
        self.assertEqual(use_pygments_css, False)

    def test_pygments_noclasses(self):
        s = settings.Settings(
            settings_path=os.path.join('tests', 'settings', 'pygments_noclasses.cfg')
        )
        s.read_settings()
        new_s = s.get('Untitled')

        use_pygments_css = new_s.get('settings').get('use_pygments_css')
        self.assertEqual(use_pygments_css, False)

    def test_pygments_class(self):
        s = settings.Settings(
            settings_path=os.path.join('tests', 'settings', 'pygments_class.cfg')
        )
        s.read_settings()
        new_s = s.get('Untitled')

        pygments_css = new_s.get('settings').get('pygments_class')
        self.assertEqual(pygments_css, 'highlight')
