#!/usr/bin/env python
"""
Mdown logger

Simple class for controlling when to log to stdout

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import print_function


class Logger(object):
    """ Log messages """
    quiet = False

    @classmethod
    def log(cls, msg):
        """ Log if not quiet """

        if not cls.quiet:
            print(msg)