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
from os.path import join, exists, abspath, dirname, isfile, expanduser, basename
from os import listdir, mkdir
from .logger import Logger
import codecs
import traceback
import re
import yaml

RESOURCE_PATH = abspath(join(dirname(__file__), ".."))
WIN_DRIVE = re.compile(r"(^[A-Za-z]{1}:(?:\\|/))")
DATA_FOLDER = "data"
DEFAULT_CSS = "data/default-markdown.css"
DEFAULT_TEMPLATE = "data/default-template.html"
DEFAULT_SETTINGS = "data/pymdown.cfg"
USER_VERSION = "data/version.txt"
NO_COPY = ('licenses.txt',)
NO_UPDATE = (basename(DEFAULT_SETTINGS),)
NOT_DEFAULT = (basename(DEFAULT_SETTINGS), 'version.txt')

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def get_encoding(enc):
    try:
        codecs.lookup(enc)
    except LookupError:
        enc = 'utf-8'
    return enc


def is_absolute(pth):
    """ Check if path is an absolute path. """
    absolute = False
    if pth is not None:
        if sys.platform.startswith('win'):
            if WIN_DRIVE.match(pth) is not None or pth.startswith("//"):
                absolute = True
        elif pth.startswith('/'):
            absolute = True
    return absolute


def get_user_path():
    """
    Get user data path
    """

    if _PLATFORM == "windows":
        folder = expanduser("~\\.PyMdown")
    elif _PLATFORM == "osx":
        folder = expanduser("~/Library/Application Support/PyMdown")
    elif _PLATFORM == "linux":
        folder = expanduser("~/.config/PyMdown")

    if not exists(folder):
        try:
            mkdir(folder)
        except:
            pass

    defaults = join(folder, 'default')
    if not exists(defaults):
        try:
            mkdir(defaults)
        except:
            pass

    return folder


def update_user_files():
    """ See if user data files should be updated """
    user_ver_file = join(get_user_path(), 'version.txt')
    ver = load_text_resource(USER_VERSION, internal=True)
    if ver is not None:
        try:
            current_ver = yaml.load(ver).get('version', 0)
        except:
            current_ver = 0
    try:
        with codecs.open(user_ver_file, 'r', encoding='utf-8') as f:
            user_ver = yaml.load(f.read()).get('version', 0)
    except:
        user_ver = 0

    return current_ver != user_ver


def unpack_user_files():
    """ Unpack user data files """
    user_path = get_user_path()
    folder = resource_exists(DATA_FOLDER, internal=True, dir=True)
    should_update = update_user_files()
    if folder is not None:
        for f in listdir(folder):
            if f in NOT_DEFAULT:
                dest = join(user_path, basename(f))
            else:
                dest = join(user_path, 'default', basename(f))
            source = join(folder, f)
            if isfile(source) and f not in NO_COPY:
                if not exists(dest) or (should_update and f not in NO_UPDATE):
                    text = load_text_resource(source, internal=True)
                    if text is not None:
                        try:
                            with codecs.open(dest, "w", encoding='utf-8') as f:
                                f.write(text)
                        except:
                            pass


def splitenc(entry, default='utf-8'):
    """ Split encoding from file name """
    parts = entry.split(';')
    if len(parts) > 1:
        entry = ';'.join(parts[:-1])
        encoding = get_encoding(parts[-1])
    else:
        encoding = get_encoding(default)
    return entry, encoding


def load_egg_resources():
    """
    Add egg to system path if the name indicates it
    is for the current python version and for pymdown.
    This only runs if we are not in a pyinstaller environment.
    """
    if (
        not bool(getattr(sys, "frozen", 0)) and
        exists('eggs') and not isfile('eggs')
    ):
        egg_extension = "py%d.%d.egg" % (
            sys.version_info.major, sys.version_info.minor
        )
        egg_start = "pymdown"
        for f in listdir("eggs"):
            target = abspath(join('eggs', f))
            if (
                isfile(target) and f.endswith(egg_extension) and
                f.startswith(egg_start)
            ):
                sys.path.append(target)


def resource_exists(*args, **kwargs):
    """ If resource could be found return path else None """

    if kwargs.get('internal', False):
        base = None
        if getattr(sys, "frozen", 0):
            base = sys._MEIPASS
        else:
            base = RESOURCE_PATH

        path = join(base, *args)
    else:
        path = join(*args)

    directory = kwargs.get('dir', False)

    if not exists(path) or (not isfile(path) if not directory else isfile(path)):
        path = None

    return path


def load_text_resource(*args, **kwargs):
    """ Load text resource from either the package source location """
    path = resource_exists(*args, **kwargs)

    encoding = get_encoding(kwargs.get('encoding', 'utf-8'))

    data = None
    if path is not None:
        try:
            with codecs.open(path, "rb") as f:
                data = f.read().decode(encoding).replace('\r', '')
        except:
            Logger.debug(traceback.format_exc())
            pass
    return data
