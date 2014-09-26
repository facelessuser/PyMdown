from __future__ import unicode_literals
from markdown import Extension

extensions = [
    'pymdown.delete',
    'pymdown.githubemoji',
    'pymdown.magiclink',
    'pymdown.tasklist',
    'pymdown.headeranchor',
    'pymdown.betterem',
    'markdown.extensions.nl2br'
]


class GithubExtension(Extension):
    """Add various extensions to Markdown class"""

    def extendMarkdown(self, md, md_globals):
        """Register extension instances"""
        md.registerExtensions(extensions, self.config)


def makeExtension(*args, **kwargs):
    return GithubExtension(*args, **kwargs)
