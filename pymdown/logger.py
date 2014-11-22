#!/usr/bin/env python
"""
PyMdown logger

Simple class for controlling when to log to stdout

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
import logging
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG
logger = logging.getLogger('PYMDOWN')
logger.setLevel(INFO)
logger.addHandler(logging.StreamHandler())

__all__ = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "Log"]


class Log(object):
    """ Log messages """

    @classmethod
    def set_level(cls, lvl):
        logger.setLevel(lvl)

    @classmethod
    def info(cls, msg):
        logger.info(msg)

    @classmethod
    def warn(cls, msg):
        logger.warn(msg)

    @classmethod
    def error(cls, msg):
        logger.error(msg)

    @classmethod
    def debug(cls, msg):
        logger.debug(msg)

    @classmethod
    def crit(cls, msg):
        logger.critical(msg)
