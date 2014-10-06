#!/usr/bin/env python

from setuptools import setup, find_packages

entry_points = '''
[pygments.lexers]
'''

setup(
    name='pymdown-lexers',
    version='1.0',
    packages=find_packages(),
    entry_points=entry_points,
    zip_safe=True
)
