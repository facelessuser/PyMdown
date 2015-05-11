from __future__ import unicode_literals
import unittest
from collections import OrderedDict
from pymdown import util
from pymdown import settings
from pymdown import logger
import os


class TestSettings(unittest.TestCase):
    def _get_settings(self, settings_file, **kwargs):
        kwargs['settings_path'] = os.path.join('tests', 'settings', settings_file)
        s = settings.Settings(**kwargs)
        s.read_settings()
        return s

    def test_critic_prevent_override(self):
        s = self._get_settings(
            'critic.cfg',
            stream=True,
            critic=util.CRITIC_ACCEPT,
        ).get(None)
        option = s.get('settings').get('extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'accept')

    def test_critic_allow_override(self):
        s = self._get_settings(
            'critic.cfg',
            stream=True
        ).get(None)
        option = s.get('settings').get('extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'reject')

    def test_critic_frontmatter_override(self):
        s = self._get_settings(
            'critic.cfg',
            stream=True
        ).get(
            None,
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
        option = s.get('settings').get('extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'accept')

    def test_critic_reject(self):
        s = self._get_settings(
            'critic.cfg',
            stream=True,
            critic=util.CRITIC_REJECT
        ).get(None)
        option = s.get('settings').get('extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'reject')

    def test_critic_view(self):
        s = self._get_settings(
            'critic.cfg',
            stream=True,
            critic=util.CRITIC_VIEW
        ).get(None)
        options = s.get('settings').get('extensions').get('pymdownx.critic')
        self.assertEqual(options.get('mode'), 'view')

    def test_plain_prevent_override(self):
        s = self._get_settings(
            'plain.cfg',
            plain=True,
            stream=True
        ).get(None)
        options = s.get('settings').get('extensions').get('pymdownx.plainhtml')
        self.assertEqual(options, None)

    def test_plain_allow_override(self):
        s = self._get_settings(
            'plain.cfg',
            stream=True
        ).get(None)
        options = s.get('settings').get('extensions').get('pymdownx.plainhtml')
        self.assertEqual(options.get('strip_comments'), False)

    def test_pygments_no_style(self):
        s = self._get_settings(
            'pygments_no_style.cfg',
            stream=True
        ).get(None)
        style = s.get('settings').get('style')
        self.assertEqual(style, 'default')
        pygments_css = s.get('settings').get('pygments_class')
        self.assertEqual(pygments_css, 'codehilite')

    def test_pygments_bad_style(self):
        logger.Log.set_level(logger.CRITICAL)
        s = self._get_settings(
            'pygments_bad_style.cfg',
            stream=True
        ).get(None)
        style = s.get('settings').get('style')
        logger.Log.set_level(logger.INFO)
        self.assertEqual(style, 'default')

    def test_no_pygments(self):
        s = self._get_settings(
            'no_pygments.cfg',
            stream=True
        ).get(None)
        use_pygments_css = s.get('settings').get('use_pygments_css')
        self.assertEqual(use_pygments_css, False)

    def test_pygments_noclasses(self):
        s = self._get_settings(
            'pygments_noclasses.cfg',
            stream=True
        ).get(None)
        use_pygments_css = s.get('settings').get('use_pygments_css')
        self.assertEqual(use_pygments_css, False)

    def test_pygments_class(self):
        s = self._get_settings(
            'pygments_class.cfg',
            stream=True
        ).get(None)
        pygments_css = s.get('settings').get('pygments_class')
        self.assertEqual(pygments_css, 'highlight')

    def test_preview(self):
        s = self._get_settings(
            'preview_with_pathconverter.cfg',
            preview=True,
            stream=True
        ).get(None)
        options = s.get('settings').get('extensions').get('pymdownx.pathconverter')
        self.assertEqual(options.get('relative_path'), '${OUTPUT}')

    def test_preview_pathconverter(self):
        s = self._get_settings(
            'empty.cfg',
            preview=True,
            stream=True
        ).get(None)
        options = s.get('settings').get('extensions').get('pymdownx.pathconverter')
        self.assertEqual(options.get('relative_path'), '${OUTPUT}')
        self.assertEqual(options.get('base_path'), '${BASE_PATH}')
