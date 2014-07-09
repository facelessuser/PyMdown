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
import re

__version_info__ = (0, 3, 1)
__version__ = '.'.join(map(str, __version_info__))

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

CRITIC_IGNORE = 0
CRITIC_ACCEPT = 1
CRITIC_REJECT = 2
CRITIC_VIEW = 4
CRITIC_DUMP = 8
CRITIC_OFF = 16


class Logger(object):
    """ Log messages """
    quiet = False

    @classmethod
    def log(cls, msg):
        """ Log if not quiet """

        if not cls.quiet:
            print(msg)


class CriticDump(object):
    RE_CRITIC = re.compile(
        r'''
            ((?P<open>\{)
                (?:
                    (?P<ins_open>\+{2})(?P<ins_text>.*?)(?P<ins_close>\+{2})
                  | (?P<del_open>\-{2})(?P<del_text>.*?)(?P<del_close>\-{2})
                  | (?P<mark_open>\={2})(?P<mark_text>.*?)(?P<mark_close>\={2})
                  | (?P<comment>(?P<com_open>\>{2})(?P<com_text>.*?)(?P<com_close>\<{2}))
                  | (?P<sub_open>\~{2})(?P<sub_del_text>.*?)(?P<sub_mid>\~\>)(?P<sub_ins_text>.*?)(?P<sub_close>\~{2})
                )
            (?P<close>\})|.)
        ''',
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    def process(self, m):
        if self.accept:
            if m.group('ins_open'):
                return m.group('ins_text')
            elif m.group('del_open'):
                return ''
            elif m.group('mark_open'):
                return m.group('mark_text')
            elif m.group('com_open'):
                return ''
            elif m.group('sub_open'):
                return m.group('sub_ins_text')
            else:
                return m.group(0)
        else:
            if m.group('ins_open'):
                return ''
            elif m.group('del_open'):
                return m.group('del_text')
            elif m.group('mark_open'):
                return m.group('mark_text')
            elif m.group('com_open'):
                return ''
            elif m.group('sub_open'):
                return m.group('sub_del_text')
            else:
                return m.group(0)

    def dump(self, source, accept):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = ''
        self.accept = accept
        for m in self.RE_CRITIC.finditer(source):
            text += self.process(m)
        return text


def get_settings(file_name, preview, critic_mode, plain):
    """
    Get the settings and add absolutepath
    extention if a preview is planned.
    Unpack the settings file if needed.
    """

    status = 0
    # Use default file if one was not provided
    if file_name is None or not exists(file_name):
        file_name = join(script_path, "mdown.json")

    # Unpack default settings file if needed
    if not exists(file_name):
        text = load_text_resource("mdown.json")
        try:
            with codecs.open(file_name, "w", encoding="utf-8") as f:
                f.write(text)
        except:
            Logger.log(traceback.format_exc())

    # Try and read settings file
    settings = {}
    try:
        with open(file_name, "r") as f:
            settings = json.loads(sanitize_json(f.read()))
    except:
        Logger.log(traceback.format_exc())
        status = 1

    absolute = False
    critic_found = []
    plain_html = []
    extensions = settings.get("extensions", [])
    for i in range(0, len(extensions)):
        name = extensions[i]
        if name.startswith("mdownx.absolutepath"):
            absolute = True
        if name.startswith("critic"):
            critic_found.append(i)
        if name.startswith("mdownx.plainhtml"):
            plain_html.append(i)

    # Ensure the user can never set critic mode
    for index in reversed(critic_found):
        del extensions[index]

    # Ensure the user can never set plainhtml mode
    for index in reversed(plain_html):
        del extensions[index]

    # Ensure previews are using absolute paths
    if preview and not absolute:
        extensions.append("mdownx.absolutepath(base_path=${BASE_PATH})")

    # Handle the appropriate critic mode internally
    # Critic must be appended to end of extension list
    if critic_mode != CRITIC_OFF:
        mode = "ignore"
        if critic_mode & CRITIC_ACCEPT:
            mode = "accept"
        elif critic_mode & CRITIC_REJECT:
            mode = "reject"
        extensions.append("mdownx.critic(mode=%s)" % mode)

    # Handle plainhtml internally.  Must be appended to the end. Okay to come after critic.
    if plain:
        extensions.append("mdownx.plainhtml")

    settings["extensions"] = extensions

    return status, settings


def get_title(md_file, title_val, is_stream):
    """ Get title for HTML """
    if title_val is not None:
        title = title_val
    elif not is_stream:
        title = basename(abspath(md_file))
    else:
        title = None
    return title


def get_output(md_file, index, output_val, terminal, is_stream, critic_mode):
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

    critic_enabled = critic_mode & CRITIC_ACCEPT or critic_mode & CRITIC_REJECT
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
                if critic_mode & CRITIC_DUMP and critic_enabled:
                    if critic_mode & CRITIC_REJECT:
                        label = ".rejected"
                    else:
                        label = ".accepted"
                    base, ext = splitext(abspath(md_file))
                    output = join(name, "%s%s%s" % (base, label, ext))
                else:
                    output = join(name, "%s.html" % splitext(abspath(md_file))[0])
            else:
                # Stream: don't know what the file should be called
                output = None
        else:
            # Apply mult-pattern to name
            output = name.replace("${count}", index)
    elif not is_stream:
        if critic_mode & CRITIC_DUMP and critic_enabled:
            if critic_mode & CRITIC_REJECT:
                label = ".rejected"
            else:
                label = ".accepted"
            base, ext = splitext(abspath(md_file))
            output = "%s%s%s" % (base, label, ext)
        else:
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
    assert len(file_patterns), "No file patterns"
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


def critic_dump(md_file, enc, out, stream, reject):
    """ Process the critic marks and dump the modified file """

    status = 0
    text = None
    try:
        if not stream:
            with codecs.open(md_file, "r", encoding=enc) as f:
                text = CriticDump().dump(f.read(), not reject)
        else:
            text = CriticDump().dump(md_file, not reject)
    except:
        Logger.log(traceback.format_exc())
        status = 1
    if text is not None:
        if out is not None:
            try:
                if out is not None:
                    with codecs.open(out, "w", encoding=enc) as f:
                        f.write(text)
            except:
                status = 1
                print(text.encode(enc))
        else:
            print(text.encode(enc))
    return status


def html_dump(md_file, enc, out, stream, html_title, base_path, preview, plain, settings):
    """ Dump HTML """

    status = 0
    # Instantiate Mdown class
    mdown = (Mdowns if stream else Mdown)(
        md_file, enc,
        title=html_title, base_path=base_path, plain=plain,
        settings=settings
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


def display_licenses():
    status = 0
    text = load_text_resource("LICENSE")
    if text is not None:
        print(text)
    else:
        status = 1
    print("")
    print("Idea based off of the Markdown Preview plugin:")
    print("https://github.com/revolunet/sublimetext-markdown-preview")
    print("http://revolunet.mit-license.org/")
    print("")
    print("\n===== 3rd Party Licenses =====")
    print("Markdown - https://pythonhosted.org/Markdown/")
    text = load_text_resource("markdown", "LICENSE.md")
    if text is not None:
        print(text)
    else:
        status = 1
    print("")
    print("Pygments - http://pygments.org/")
    text = load_text_resource("pygments", "LICENSE")
    if text is not None:
        print(text)
    else:
        status = 1
    print("")
    print("highlight.js - http://highlightjs.org/")
    text = load_text_resource("highlight.js", "LICENSE")
    if text is not None:
        print(text)
    else:
        status = 1
    return status


def convert(
    markdown=[], title=None, encoding="utf-8",
    output=None, basepath=None, preview=False,
    terminal=False, quiet=False,
    text_buffer=None, critic_mode=CRITIC_IGNORE,
    settings_path=None, plain=False
):
    """ Convert markdown file(s) to html """
    status = 0
    Logger.quiet = quiet

    # Get file(s) or stream
    files = None
    stream = False

    if text_buffer is not None:
        stream = True
        files = [text_buffer]
    else:
        try:
            files = get_files(markdown)
        except:
            files = [get_file_stream(encoding)]
            stream = True

    # Make sure we have something we can process
    if files is None or len(files) == 0 or files[0] in ('', None):
        Logger.log("Nothing to parse!")
        status = 1

    if status == 0:
        count = 0
        for md_file in files:
            # Quit dumping if there was an error
            if status != 0:
                break

            if stream:
                Logger.log("Converting buffer...")
            else:
                Logger.log("Converting %s..." % md_file)

            # Get base path to use when resolving basepath paths
            base_path = get_base_path(md_file, basepath, stream)

            # Get output location
            out = get_output(
                md_file, count, output, terminal, stream, critic_mode
            )

            # Get the title to be used in the HTML
            html_title = get_title(md_file, title, stream)

            # Get the settings if available
            status, settings = get_settings(
                settings_path, preview, critic_mode, plain
            )

            if status == 0:
                if critic_mode & CRITIC_DUMP:
                    if not (critic_mode & CRITIC_REJECT or critic_mode & CRITIC_ACCEPT):
                        Logger.log("Acceptance or rejection was not specified for critic dump!")
                        status = 1
                    else:
                        status = critic_dump(md_file, encoding, out, stream, critic_mode & CRITIC_REJECT)
                else:
                    status = html_dump(
                        md_file, encoding, out, stream, html_title,
                        base_path, preview, plain, settings
                    )
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
        parser.add_argument('--licenses', action='store_true', default=False, help="Display licenses.")
        parser.add_argument('--quiet', '-q', action='store_true', default=False, help="No messages on stdout.")
        # Format and Viewing
        parser.add_argument('--preview', '-p', action='store_true', default=False, help="Output to preview (temp file). --output will be ignored.")
        parser.add_argument('--plain-html', '-P', action='store_true', default=False, help="Strip out CSS, style, ids, etc.  Just show tags.")
        parser.add_argument('--title', nargs=1, default=None, help="Title for HTML.")
        # Critic features
        critic_group = parser.add_mutually_exclusive_group()
        critic_group.add_argument('--accept', '-a', action='store_true', default=False, help="Accept propossed critic marks when using in normal processing and --critic-dump processing")
        critic_group.add_argument('--reject', '-r', action='store_true', default=False, help="Reject propossed critic marks when using in normal processing and --critic-dump processing")
        parser.add_argument('--critic-dump', action='store_true', default=False, help="Process critic marks, dumps file(s), and exits.")
        parser.add_argument('--no-critic', action='store_true', default=False, help="Turn off critic feature completely")
        # Output
        parser.add_argument('--terminal', '-t', action='store_true', default=False, help="Print to terminal (stdout).")
        parser.add_argument('--output', '-o', nargs=1, default=None, help="Output directory can be a directory or file_name.  Use ${count} when exporting multiple files and using a file pattern.")
        parser.add_argument('--batch', '-b', action='store_true', default=False, help="Batch mode output.")
        # Input configuration
        parser.add_argument('--settings', '-s', nargs=1, default=None, help="Load the settings file from an alternate location.")
        parser.add_argument('--encoding', '-e', nargs=1, default=["utf-8"], help="Encoding for input.")
        parser.add_argument('--basepath', nargs=1, default=None, help="The basepath location mdown should use.")
        parser.add_argument('markdown', nargs='*', default=[], help="Markdown file(s) or file pattern(s).")

        args = parser.parse_args()

        if args.licenses:
            return display_licenses()

        critic_mode = CRITIC_IGNORE

        if args.no_critic:
            if args.accept or args.reject:
                critic_mode |= CRITIC_ACCEPT if args.accept else CRITIC_REJECT

            if args.critic_dump:
                critic_mode |= CRITIC_DUMP
        else:
            critic_mode |= CRITIC_OFF

        return convert(
            encoding=args.encoding[0],
            basepath=first_or_none(args.basepath),
            terminal=args.terminal,
            critic_mode=critic_mode,
            title=first_or_none(args.title),
            quiet=args.quiet,
            preview=args.preview,
            output=first_or_none(args.output),
            settings_path=first_or_none(args.settings),
            markdown=args.markdown,
            plain=args.plain_html
        )

    script_path = dirname(abspath(sys.argv[0]))
    try:
        sys.exit(main())
    except (KeyboardInterrupt, SystemExit):
        sys.exit(1)
else:
    script_path = dirname(abspath(__file__))
