from __future__ import print_function


class Logger(object):
    """ Log messages """
    quiet = False

    @classmethod
    def log(cls, msg):
        """ Log if not quiet """

        if not cls.quiet:
            print(msg)