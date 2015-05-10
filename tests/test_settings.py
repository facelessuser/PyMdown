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
