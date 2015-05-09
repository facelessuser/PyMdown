#!/usr/bin/env python
"""
PyMdown  CLI

Front end CLI that allows the batch conversion of
markdown files to HTML.  Also accepts an input stream
for piping markdown.

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import print_function

import argparse
import sys
import traceback
import os.path as path
from . import pymdown
from . import resources as res
from . import logger
from . import settings
from .compat import stdout_write, to_unicode

__version__ = '.'.join(map(str, pymdown.version_info))


def get_files(file_patterns):
    """ Find and return files matching the given patterns """

    import glob
    files = []
    all_files = set()
    assert len(file_patterns), "No file patterns"
    if len(file_patterns):
        for pattern in file_patterns:
            files += glob.glob(pattern)
    for f in files:
        all_files.add(path.abspath(path.normpath(f)))
    return list(all_files)


def get_file_stream(encoding):
    """ Get the file stream """

    import fileinput
    sys.argv = []
    text = []
    try:
        for line in fileinput.input():
            text.append(to_unicode(line, encoding))
        stream = ''.join(text)
    except:
        logger.Log.error(traceback.format_exc())
        stream = None
    text = None
    return stream


def get_critic_mode(args):
    """ Setp the critic mode """
    critic_mode = settings.CRITIC_IGNORE
    if args.accept and args.reject:
        critic_mode |= settings.CRITIC_VIEW
    elif args.accept:
        critic_mode |= settings.CRITIC_ACCEPT
    elif args.reject:
        critic_mode |= settings.CRITIC_REJECT
    if args.critic_dump:
        critic_mode |= settings.CRITIC_DUMP
    return critic_mode


def get_sources(args):
    """ Get file(s) or stream """
    files = None
    stream = False

    try:
        files = get_files(args.markdown)
    except:
        files = [get_file_stream(args.encoding)]
        stream = True
    return files, stream


def display_licenses():
    """ Display licenses """
    status = pymdown.PASS
    text = res.load_text_resource(path.join('pymdown', 'data', 'licenses.txt'), internal=True)
    if text is not None:
        stdout_write(text.encode('utf-8'))
    else:
        status = pymdown.FAIL
    return status


def main():
    """ Go! """

    parser = argparse.ArgumentParser(prog='pymdown', description='Markdown generator')
    # Flag arguments
    parser.add_argument('--version', action='version', version="%(prog)s " + __version__)
    parser.add_argument('--debug', '-d', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('--licenses', action='store_true', default=False, help="Display licenses.")
    parser.add_argument('--quiet', '-q', action='store_true', default=False, help="No messages on stdout.")
    # Format and Viewing
    parser.add_argument('--preview', '-p', action='store_true', default=False, help="Output to preview (temp file). --output will be ignored.")
    parser.add_argument('--plain-html', '-P', action='store_true', default=False, help="Strip out CSS, style, ids, etc.  Just show tags.")
    parser.add_argument('--title', default=None, help="Title for HTML.")
    # Critic features
    parser.add_argument('--accept', '-a', action='store_true', default=False, help="Accept propossed critic marks when using in normal processing and --critic-dump processing")
    parser.add_argument('--reject', '-r', action='store_true', default=False, help="Reject propossed critic marks when using in normal processing and --critic-dump processing")
    parser.add_argument('--critic-dump', action='store_true', default=False, help="Process critic marks, dumps file(s), and exits.")
    # Output
    parser.add_argument('--output', '-o', default=None, help="Output file. Ignored in batch mode.")
    parser.add_argument('--batch', '-b', action='store_true', default=False, help="Batch mode output.")
    parser.add_argument('--force-stdout', action='store_true', default=False, help="Force output to stdout.")
    parser.add_argument('--force-no-template', action='store_true', default=False, help="Force using no template.")
    parser.add_argument('--output-encoding', '-E', default=None, help="Output encoding.")
    parser.add_argument('--clean', '-c', action='store_true', default=False, help=argparse.SUPPRESS)
    # Input configuration
    parser.add_argument('--settings', '-s', default=path.join(res.get_user_path(), "pymdown.cfg"), help="Load the settings file from an alternate location.")
    parser.add_argument('--encoding', '-e', default="utf-8", help="Encoding for input.")
    parser.add_argument('--basepath', default=None, help="The basepath location pymdown should use.")
    parser.add_argument('--relpath', default=None, help="The path that things will be relative to (default is output).")
    parser.add_argument('markdown', nargs='*', default=[], help="Markdown file(s) or file pattern(s).")

    args = parser.parse_args()

    if args.licenses:
        sys.exit(display_licenses())

    if args.debug:
        logger.Log.set_level(logger.CRITICAL if args.quiet else logger.DEBUG)
    else:
        logger.Log.set_level(logger.CRITICAL if args.quiet else logger.INFO)

    files, stream = get_sources(args)
    if stream:
        batch = False
    else:
        batch = args.batch

    if not batch and len(files) > 1:
        logger.Log.log("Please use batch mode to process multiple files!")
        sys.exit(pymdown.FAIL)

    # It is assumed that the input encoding is desired for output
    # unless otherwise specified.
    if args.output_encoding is None:
        args.output_encoding = args.encoding

    # Convert
    sys.exit(
        pymdown.Convert(
            basepath=args.basepath,
            relpath=args.relpath,
            title=args.title,
            output=args.output,
            encoding=args.encoding,
            output_encoding=args.output_encoding,
            critic=get_critic_mode(args),
            batch=batch,
            stream=stream,
            preview=args.preview,
            settings_path=args.settings,
            plain=args.plain_html,
            force_stdout=args.force_stdout,
            force_no_template=args.force_no_template,
            clean=args.clean
        ).convert(files)
    )

if __name__ == '__main__':
    main()
