"""Test the settings lib."""
from __future__ import unicode_literals
import unittest
from collections import OrderedDict
from pymdown import util
from pymdown import settings
from pymdown import logger
import os


class TestSettings(unittest.TestCase):
    """TestSettings."""

    def _get_settings(self, settings_file, **kwargs):
        """Retrieve the desired test config file."""

        kwargs['settings_path'] = os.path.join('tests', 'settings', settings_file)
        s = settings.Settings(**kwargs)
        s.read_settings()
        return s

    def test_critic_prevent_override(self):
        """Test that we prevent critic override if critic is specified from command line."""

        s = self._get_settings(
            'critic.yml',
            stream=True,
            critic=util.CRITIC_ACCEPT,
        ).get(None)
        option = s.get('pymdown_settings').get('markdown_extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'accept')

    def test_critic_allow_override(self):
        """Test that we can override critic option if not already specified."""

        s = self._get_settings(
            'critic.yml',
            stream=True
        ).get(None)
        option = s.get('pymdown_settings').get('markdown_extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'reject')

    def test_critic_frontmatter_override(self):
        """Test that the frontmatter can override the critic option."""

        s = self._get_settings(
            'critic.yml',
            stream=True
        ).get(
            None,
            frontmatter=OrderedDict(
                [('pymdown_settings', OrderedDict(
                    [('markdown_extensions', OrderedDict(
                        [('pymdownx.critic', OrderedDict(
                            [('mode', 'accept')]
                        ))]
                    ))]
                ))]
            )
        )
        option = s.get('pymdown_settings').get('markdown_extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'accept')

    def test_critic_reject(self):
        """Test that we can set the critic reject option."""

        s = self._get_settings(
            'critic.yml',
            stream=True,
            critic=util.CRITIC_REJECT
        ).get(None)
        option = s.get('pymdown_settings').get('markdown_extensions').get('pymdownx.critic').get('mode')
        self.assertEqual(option, 'reject')

    def test_critic_view(self):
        """Test that we can set the critic view option."""

        s = self._get_settings(
            'critic.yml',
            stream=True,
            critic=util.CRITIC_VIEW
        ).get(None)
        options = s.get('pymdown_settings').get('markdown_extensions').get('pymdownx.critic')
        self.assertEqual(options.get('mode'), 'view')

    def test_plain_prevent_override(self):
        """Test that we can prevent the plain override if plain is set from command line."""

        s = self._get_settings(
            'plain.yml',
            plain=True,
            stream=True
        ).get(None)
        options = s.get('pymdown_settings').get('markdown_extensions').get('pymdownx.plainhtml')
        self.assertEqual(options, None)

    def test_plain_allow_override(self):
        """Test that we can override the plain setting if not already set."""

        s = self._get_settings(
            'plain.yml',
            stream=True
        ).get(None)
        options = s.get('pymdown_settings').get('markdown_extensions').get('pymdownx.plainhtml')
        self.assertEqual(options.get('strip_comments'), False)

    def test_pygments_no_style(self):
        """Ensure we get default style if none is specified."""

        s = self._get_settings(
            'pygments_no_style.yml',
            stream=True
        ).get(None)
        style = s.get('pymdown_settings').get('pygments_style')
        self.assertEqual(style, 'default')

    def test_pygments_bad_style(self):
        """Ensure we fallback to default style if a bad style is specified."""

        logger.Log.set_level(logger.CRITICAL)
        s = self._get_settings(
            'pygments_bad_style.yml',
            stream=True
        ).get(None)
        style = s.get('pymdown_settings').get('pygments_style')
        logger.Log.set_level(logger.INFO)
        self.assertEqual(style, 'default')

    def test_pygments_class(self):
        """Ensure we can set the Pygments css class internally."""

        s = self._get_settings(
            'pygments_class.yml',
            stream=True
        ).get(None)
        pygments_css = s.get('pymdown_settings').get('pygments_class')
        self.assertEqual(pygments_css, 'highlight')

    def test_preview(self):
        """Test that we set relative path proper when preview mode is true with pathconverter."""

        s = self._get_settings(
            'preview_with_pathconverter.yml',
            preview=True,
            stream=True
        ).get(None)
        options = s.get('pymdown_settings').get('markdown_extensions').get('pymdownx.pathconverter')
        self.assertEqual(options.get('relative_path'), '${OUTPUT}')

    def test_preview_pathconverter(self):
        """Ensure we configure pathconverter when not already configured when preview is enabled."""

        s = self._get_settings(
            'empty.yml',
            preview=True,
            stream=True
        ).get(None)
        options = s.get('pymdown_settings').get('markdown_extensions').get('pymdownx.pathconverter')
        self.assertEqual(options.get('relative_path'), '${OUTPUT}')
        self.assertEqual(options.get('base_path'), '${BASE_PATH}')

    def test_output_path(self):
        """
        Test that relative path based on output path.

            - relpath should == base when relpath is not set.
            - If relpath is provided, it should get set proper.
        """

        base = os.path.abspath('.')
        rel = os.path.join(os.path.abspath('.'), 'tests')
        sobj = self._get_settings(
            'empty.yml'
        )
        s = sobj.get('test.md')
        self.assertEqual(sobj.out, base)
        self.assertEqual(s.get('page').get('relpath'), base)

        s = sobj.get('test.md', relpath=rel)
        self.assertEqual(sobj.out, base)
        self.assertEqual(s.get('page').get('relpath'), rel)

    def test_output_frontmatter_path(self):
        """
        Ensure paths make sense when frontmatter overrides output path.

            - relpath should == frontmatter destination dir when relpath is not set.
            - If relpath is provided, it should get set proper.
        """

        dest = os.path.join(os.path.abspath('.'), 'tests', 'file.html')
        rel = os.path.abspath('.')
        sobj = self._get_settings(
            'empty.yml'
        )
        s = sobj.get('test.md', frontmatter={"destination": dest})
        self.assertEqual(sobj.out, os.path.dirname(dest))
        self.assertEqual(s.get('page').get('relpath'), os.path.dirname(dest))

        s = sobj.get('test.md', relpath=rel, frontmatter={"destination": dest})
        self.assertEqual(sobj.out, os.path.dirname(dest))
        self.assertEqual(s.get('page').get('relpath'), rel)

    def test_special_flags(self):
        """Ensure that the --force_stdout and --force-no-template switches are respected."""

        dest = os.path.join(os.path.abspath('.'), 'tests', 'file.html')
        template = '/'.join(['pymdown', 'data', 'template.html'])
        s = self._get_settings(
            'template.yml'
        ).get('test.md', frontmatter={"destination": dest})
        self.assertEqual(s.get('page').get('destination'), dest)
        self.assertEqual(s.get('pymdown_settings').get('template'), template)

        s = self._get_settings(
            'template.yml',
            force_stdout=True,
            force_no_template=True
        ).get('test.md', frontmatter={"destination": dest})
        self.assertEqual(s.get('page').get('destination'), None)
        self.assertEqual(s.get('pymdown_settings').get('template'), None)
