#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys

LONG_DESC = '''
PyMdown is a CLI batch Markdown conversion / preview tool.
The project utilizes Python Markdown to convert Markdown
files to HTML and includes a number of custom extensions
to add additional features and syntax to the Markdown. It
uses Pygments for the sytax highlighting code blocks.

The project repo is found at:
https://github.com/facelessuser/PyMdown.
'''

setup(
    name='PyMdown',
    version='0.8.0',
    keywords='markdown html batch',
    description='CLI Markdown batch converter/previewer.',
    long_description=LONG_DESC,
    author='Isaac Muse',
    author_email='Isaac.Muse [at] gmail.com',
    url='https://github.com/facelessuser/PyMdown',
    packages=find_packages(exclude=['pyinstaller*']),
    install_requires=[
        'Markdown>=2.6.0',
        'Pygments>=2.0.1',
        'pymdown-extensions>=1.0.0',
        'pymdown-lexers>=1.0.0',
        'pymdown-styles>=1.0.0'
    ],
    zip_safe=False,
    dependency_links=[
        'https://github.com/facelessuser/pymdown-extensions/archive/master.zip#egg=pymdown-extensions-1.0.0',
        'https://github.com/facelessuser/pymdown-lexers/archive/master.zip#egg=pymdown-lexers-1.0.0',
        'https://github.com/facelessuser/pymdown-styles/archive/master.zip#egg=pymdown-styles-1.0.0'
    ],
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
        'Development Status :: 5 - Production/Stable',
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
