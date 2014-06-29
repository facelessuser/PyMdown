#!/usr/bin/env python
"""
Mdown  CLI

Front end CLI that allows the batch conversion of
markdown files to HTML.  Also accepts an input stream
for piping markdown.

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function
from mdown import Mdown, Mdowns, load_text_resource
from os.path import dirname, abspath, normpath, exists
from os.path import isfile, isdir, splitext, join, basename
import sys
from file_strip.json import sanitize_json
import json
import subprocess
import webbrowser
import traceback
import tempfile
import codecs

__version_info__ = (0, 1, 0)
__version__ = '.'.join(map(str, __version_info__))

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


class Logger(object):
    """ Log messages """
    quiet = False

    @classmethod
    def log(cls, msg):
        """ Log if not quiet """

        if not cls.quiet:
            print(msg)


def get_settings(file_name, preview):
    """
    Get the settings and add absolutepath
    extention if a preview is planned.
    Unpack the settings file if needed.
    """

    # Unpack settings file if needed
    if not exists(file_name):
        text = load_text_resource("mdown.json")
        try:
            with codecs.open(file_name, "w", encoding="utf-8") as f:
                f.write(text)
        except:
            print(traceback.format_exc())
            pass

    # Try and read settings file
    settings = {}
    try:
        with open(file_name, "r") as f:
            settings = json.loads(sanitize_json(f.read()))
    except:
        # print(traceback.format_exc())
        pass

    # Ensure previews are using absolute paths
    if preview:
        absolute = False
        extensions = settings.get("extensions", [])
        for e in extensions:
            if e.startswith("mdownx.absolutepath"):
                absolute = True
                break
        if not absolute:
            extensions.append("mdownx.absolutepath(base_path=${BASE_PATH})")
            settings["extensions"] = extensions

    return settings


def get_title(md_file, title_val, is_stream):
    """ Get title for HTML """
    if title_val is not None:
        title = title_val
    elif not is_stream:
        title = basename(abspath(md_file))
    else:
        title = None
    return title


def get_output(md_file, index, output_val, terminal, is_stream):
    """
    Get the path to output the file.
    If doing multiple files and pointing to a directory,
    it will convert the current file name to a HTML filename
    in that directory.

    If doing multiple files and not pointing to a directory,
    it will use ${count} to have different file names.  If you
    forget this, it will rewrite the same file over and over.

    If doing a single file, and pointing to a directory, it will
    convert the current file name to a HTML filename in that directory.

    If doing a single file and not pointing to a directory, it will
    use the file path given.

    If doing a stream and pointing to a directory, the output will be
    streamed to the terminal (stdout).

    If doing a stream and not pointing to a directory, the output will
    be streamed to that file path.

    If creating the output fails by mdown or none of these conditions are met,
    the output will default to the terminal.
    """

    if terminal:
        # We want stdout
        output = None
    elif output_val is not None and output_val != "":
        # Output is specified
        name = abspath(output_val)
        if exists(name) and isdir(name):
            # Its a directory
            if not is_stream:
                # Use path and own name
                output = join(name, "%s.html" % splitext(abspath(md_file))[0])
            else:
                # Stream: don't know what the file should be called
                output = None
        else:
            # Apply mult-pattern to name
            output = name.replace("${count}", index)
    elif not is_stream:
        # Single or multi file: use own name
        output = "%s.html" % splitext(abspath(md_file))[0]
    else:
        output = None

    if not is_stream and output == md_file:
        output = None
    return output


def get_base_path(md_file, basepath, is_stream):
    """ Get the base path to use when resolving basepath paths if possible """

    if basepath is not None and exists(basepath):
        # A valid path was fed in
        path = basepath
        base_path = dirname(abspath(path)) if isfile(path) else abspath(path)
    elif not is_stream:
        # Use the current file path
        base_path = dirname(abspath(md_file))
    else:
        # Okay, there is no way to tell the orign.
        # We are probably a stream that has no specified
        # physical location.
        base_path = None
    return base_path


def get_files(file_patterns):
    """ Find and return files matching the given patterns """

    import glob
    files = []
    all_files = []
    if len(file_patterns):
        for pattern in file_patterns:
            files += glob.glob(pattern)
    for f in files:
        all_files.append(abspath(normpath(f)))
    return all_files


def get_file_stream(encoding):
    """ Get the file stream """

    import fileinput
    import traceback
    sys.argv = []
    text = []
    try:
        for line in fileinput.input():
            text.append(line.decode(encoding))
        stream = ''.join(text)
    except:
        Logger.log(traceback.format_exc())
        stream = None
    text = None
    return stream


def auto_open(name):
    """ Auto open HTML """

    # Maybe just use destop
    if _PLATFORM == "osx":
        # TODO: parse plist for default browser
        # Probably should parse com.apple.LaunchServices.plist for
        # <dict>
        #     <key>LSHandlerRoleAll</key>
        #     <string>com.google.chrome</string> <--To get this
        #     <key>LSHandlerURLScheme</key>
        #     <string>http</string>              <--Parse for this
        # </dict>
        subprocess.Popen(['open', name])
    elif _PLATFORM == "windows":
        webbrowser.open(name, new=2)
    else:
        try:
            # Maybe...?
            subprocess.Popen(['xdg-open', name])
        except OSError:
            webbrowser.open(name, new=2)
            # Well we gave it our best...
            pass


def convert(
    markdown=[], title=None, encoding="utf-8",
    output=None, basepath=None, preview=False,
    stream=False, terminal=False, quiet=False,
    text_buffer=None
):
    """ Convert markdown file(s) to html """
    status = 0
    Logger.quiet = quiet

    # Get file(s) or stream
    enc = encoding
    files = None

    if stream:
        files = [get_file_stream(enc)]
    if text_buffer is not None:
        stream = True
        files = [text_buffer]
    if files is None:
        files = get_files(markdown)

    # Make sure we have something we can process
    if files is None or len(files) == 0 or files[0] is None:
        Logger.log("No file to parse!")
        status = 1

    if status == 0:
        count = 0
        for md_file in files:
            if stream:
                Logger.log("Converting buffer...")
            else:
                Logger.log("Converting %s..." % md_file)

            # Get base path to use when resolving basepath paths
            base_path = get_base_path(md_file, basepath, stream)

            # Get output location
            out = get_output(md_file, count, output, terminal, stream)

            # Get the title to be used in the HTML
            html_title = get_title(md_file, title, stream)

            # Get the settings if available
            settings = get_settings(join(script_path, "mdown.json"), preview)

            # Instantiate Mdown class
            mdown = (Mdowns if stream else Mdown)(
                md_file, enc,
                title=html_title, base_path=base_path, settings=settings
            )

            # If all went well, either preview the file,
            # or write it to file or terminal
            if mdown.error is None:
                if preview:
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
                            f.write(mdown.markdown)
                        auto_open(f.name)
                    except:
                        Logger.log(traceback.format_exc())
                        print(mdown.markdown)
                        status = 1
                else:
                    mdown.write(out)
                if status == 0 and mdown.error is not None:
                    print(mdown.markdown)
                    Logger.log(mdown.error)
                    status = 1
            else:
                Logger.log(mdown.error)
                status = 1

    return status


if __name__ == "__main__":
    import argparse

    def first_or_none(item):
        return item[0] if item is not None else None

    def main():
        """ Go! """

        parser = argparse.ArgumentParser(prog='mdown', description='Markdown generator')
        # Flag arguments
        parser.add_argument('--version', action='version', version="%(prog)s " + __version__)
        parser.add_argument('--quiet', '-q', action='store_true', default=False, help="No messages on stdout.")
        parser.add_argument('--preview', '-p', action='store_true', default=False, help="Output to preview (temp file). --output will be ignored.")
        parser.add_argument('--terminal', '-t', action='store_true', default=False, help="Print to terminal (stdout).")
        parser.add_argument('--output', '-o', nargs=1, default=None, help="Output directory can be a directory or file_name.  Use ${count} when exporting multiple files and using a file pattern.")
        parser.add_argument('--stream', '-s', action='store_true', default=False, help="Streaming input.  markdown file inputs will be ignored.")
        parser.add_argument('--title', '-T', nargs=1, default=None, help="Title for HTML.")
        parser.add_argument('--encoding', '-e', nargs=1, default=["utf-8"], help="Encoding for input.")
        parser.add_argument('--basepath', '-b', nargs=1, default=None, help="The basepath location mdown should use.")
        parser.add_argument('markdown', nargs='*', default=[], help="Markdown file(s) or file pattern(s).")

        args = parser.parse_args()

        return convert(
            encoding=args.encoding[0],
            basepath=first_or_none(args.basepath),
            terminal=args.terminal,
            stream=args.stream,
            title=first_or_none(args.title),
            quiet=args.quiet,
            preview=args.preview,
            output=first_or_none(args.output),
            markdown=args.markdown
        )

    script_path = dirname(abspath(sys.argv[0]))
    sys.exit(main())
else:
    script_path = dirname(abspath(__file__))
