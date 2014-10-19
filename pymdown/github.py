from __future__ import unicode_literals
from markdown import Extension

extensions = [
    'markdown.extensions.tables',
    'pymdown.magiclink',
    'pymdown.betterem',
    'pymdown.tilde',
    'pymdown.githubemoji',
    'pymdown.tasklist',
    'pymdown.headeranchor',
    'pymdown.nestedfences',
    'markdown.extensions.nl2br'
]

extension_configs = {
    "pymdown.tilde": {
        "subscript": False
    }
}


class GithubExtension(Extension):
    """Add various extensions to Markdown class"""

    def extendMarkdown(self, md, md_globals):
        """Register extension instances"""
        md.registerExtensions(extensions, extension_configs)


def makeExtension(*args, **kwargs):
    return GithubExtension(*args, **kwargs)
