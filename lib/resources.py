#!/usr/bin/env python
"""
resources

Load resources from project normally or when it
is packaged via Pyinstaller

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import print_function
import sys
from os.path import join, exists, abspath, dirname, isfile
import codecs

RESOURCE_PATH = abspath(join(dirname(__file__), ".."))
DEFAULT_CSS = "default-markdown.css"
DEFAULT_TEMPLATE = "default-template.html"


def resource_exists(*args):
    """ If resource could be found return path else None """
    base = None
    try:
        base = sys._MEIPASS
    except:
        base = RESOURCE_PATH

    path = join(base, *args)

    if not exists(path) or not isfile(path):
        path = None

    return path


def load_text_resource(*args):
    """ Load text resource from either the package source location """
    path = resource_exists(*args)

    data = None
    if path is not None:
        try:
            with codecs.open(path, "rb") as f:
                data = f.read().decode("utf-8")
        except:
            # print(traceback.format_exc())
            pass
    return data
