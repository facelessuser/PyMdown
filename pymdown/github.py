from __future__ import unicode_literals
from markdown import Extension

extensions = [
    'pymdown.magiclink',
    'pymdown.betterem',
    'pymdown.tilde(subscript=False)',
    'pymdown.githubemoji',
    'pymdown.tasklist',
    'pymdown.headeranchor',
    'markdown.extensions.nl2br'
]


class GithubExtension(Extension):
    """Add various extensions to Markdown class"""

    def extendMarkdown(self, md, md_globals):
        """Register extension instances"""
        md.registerExtensions(extensions, self.config)


def makeExtension(*args, **kwargs):
    return GithubExtension(*args, **kwargs)
