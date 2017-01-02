#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup package."""
from setuptools import setup, find_packages
import sys
import os
import imp

LONG_DESC = '''
PyMdown is a CLI batch Markdown conversion / preview tool.
The project utilizes Python Markdown to convert Markdown
files to HTML and includes a number of custom extensions
to add additional features and syntax to the Markdown input. It
uses Pygments for the sytax highlighting code blocks.

The project repo is found at: https://github.com/facelessuser/PyMdown.
'''


def get_version():
    """Get version and version_info without importing the entire module."""

    devstatus = {
        'alpha': '3 - Alpha',
        'beta': '4 - Beta',
        'candidate': '4 - Beta',
        'final': '5 - Production/Stable'
    }
    path = os.path.join(os.path.dirname(__file__), 'pymdown')
    fp, pathname, desc = imp.find_module('__version__', [path])
    try:
        v = imp.load_module('__version__', fp, pathname, desc)
        return v.version, devstatus[v.version_info[3]]
    finally:
        fp.close()


VER, DEVSTATUS = get_version()

setup(
    name='PyMdown',
    version=VER,
    keywords='markdown html batch',
    description='Markdown batch converter/previewer.',
    long_description=LONG_DESC,
    author='Isaac Muse',
    author_email='Isaac.Muse [at] gmail.com',
    url='https://github.com/facelessuser/PyMdown',
    packages=find_packages(),
    install_requires=[
        'Markdown>=2.6.0,<3',
        'Pygments>=2.0.1',
        'PyYAML>=3.10',
        'Jinja2>=2.7.3',
        'pymdown-extensions>=1.0.1'
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pymdown=pymdown.cli:main',
            'pymdown%d.%d=pymdown.cli:main' % sys.version_info[:2],
        ]
    },
    package_data={
        'pymdown.data': ['*.*']
    },
    license='MIT License',
    classifiers=[
        'Development Status :: %s' % DEVSTATUS,
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
