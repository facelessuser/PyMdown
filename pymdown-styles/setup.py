#!/usr/bin/env python

from setuptools import setup, find_packages

entry_points = '''
[pygments.styles]
github=pymdown_styles:GithubStyle
github2=pymdown_styles:Github2Style
tomorrow=pymdown_styles:TomorrowStyle
tomorrownight=pymdown_styles:TomorrownightStyle
tomorrownightblue=pymdown_styles:TomorrownightblueStyle
tomorrownightbright=pymdown_styles:TomorrownightbrightStyle
tomorrownighteighties=pymdown_styles:TomorrownighteightiesStyle
'''

setup(
    name='pymdown-styles',
    version='1.0',
    packages=find_packages(),
    entry_points=entry_points
)
