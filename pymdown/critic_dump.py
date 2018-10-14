"""
Strips and returns the the markdown with critic marks removed.

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from pymdownx.critic import CriticViewPreprocessor, CriticStash, CRITIC_KEY


class CriticDump(object):
    """
    Critic Dumper.

    Dumps out content with critic marks processed or,
    in the case of 'view' mode, converts them to tags.
    """

    def dump(self, source, accept, view=False):
        """Process critic marks and return the file."""

        text = ''
        if accept:
            mode = 'accept'
        else:
            mode = 'reject'

        critic_stash = CriticStash(CRITIC_KEY)
        critic = CriticViewPreprocessor(critic_stash)
        critic.config = {'mode': mode}
        text = '\n'.join(critic.run(source.split('\n')))

        return text
