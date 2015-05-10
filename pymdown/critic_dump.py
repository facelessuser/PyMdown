"""
Strips and returns the the markdown with critic marks removed

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import absolute_import
from pymdownx.critic import CriticViewPreprocessor, CriticsPostprocessor, CriticStash, CRITIC_KEY


class CriticDump(object):
    def dump(self, source, accept, view=False):
        text = ''
        if view:
            mode = 'view'
        elif accept:
            mode = 'accept'
        else:
            mode = 'reject'

        critic_stash = CriticStash(CRITIC_KEY)
        critic = CriticViewPreprocessor(critic_stash)
        critic.config = {'mode': mode}
        text = '\n'.join(critic.run(source.split('\n')))
        if view:
            critic_post = CriticsPostprocessor(critic_stash)
            text = critic_post.run(text)

        return text
