"""
PyMdown logger.

Simple class for controlling when to log to stdout

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
import logging
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG
logger = logging.getLogger('PYMDOWN')
logger.setLevel(INFO)
logger.addHandler(logging.StreamHandler())

__all__ = ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "Log")


class Log(object):

    """Log messages."""

    @classmethod
    def set_level(cls, lvl):
        """Set the log level."""

        logger.setLevel(lvl)

    @classmethod
    def info(cls, msg):
        """Log info level."""

        logger.info(msg)

    @classmethod
    def warn(cls, msg):
        """Log warn level."""

        logger.warn(msg)

    @classmethod
    def error(cls, msg):
        """Log error level."""

        logger.error(msg)

    @classmethod
    def debug(cls, msg):
        """Log debug level."""

        logger.debug(msg)

    @classmethod
    def crit(cls, msg):
        """Log critical level."""

        logger.critical(msg)
