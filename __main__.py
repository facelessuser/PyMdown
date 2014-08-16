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
import codecs
import sys
import subprocess
import webbrowser
import traceback
from os.path import dirname, abspath, normpath, exists, basename, join
from lib.logger import Logger
from lib import critic_dump as cd
from lib.settings import Settings
from lib.resources import load_text_resource
from lib.mdown import Mdowns
from lib import formatter
from lib.frontmatter import get_frontmatter_string

__version_info__ = (0, 5, 0)
__version__ = '.'.join(map(str, __version_info__))

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

PASS = 0
FAIL = 1


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


def get_critic_mode(args):
    """ Setp the critic mode """
    critic_mode = cd.CRITIC_IGNORE
    if not args.no_critic:
        if args.accept or args.reject:
            critic_mode |= cd.CRITIC_ACCEPT if args.accept else cd.CRITIC_REJECT
        if args.critic_dump:
            critic_mode |= cd.CRITIC_DUMP
    else:
        critic_mode |= cd.CRITIC_OFF
    return critic_mode


def get_references(file_name, encoding):
    """ Get footnote and general references from outside source """
    text = ''
    if file_name is not None:
        if exists(file_name):
            try:
                with codecs.open(file_name, "r", encoding=encoding) as f:
                    text = f.read()
            except:
                Logger.log(traceback.format_exc())
        else:
            Logger.log("Could not find reference file %s!", file_name)
    return text


def get_sources(args):
    """ Get file(s) or stream """
    files = None
    stream = False

    try:
        files = get_files(args.markdown)
    except:
        files = [get_file_stream(args.encoding[0])]
        stream = True
    return files, stream


def get_title(file_name, title_val):
    """ Get title for HTML """
    if title_val is not None:
        title = str(title_val)
    elif file_name is not None:
        title = basename(abspath(file_name))
    else:
        title = None
    return title


def merge_meta(meta1, meta2, title=None):
    """ Merge meta1 and meta2.  Add title to meta data if needed. """
    meta = dict(meta1.items() + meta2.items())
    if "title" not in meta and title is not None:
        if title is not None:
            meta["title"] = title
    return meta


def display_licenses():
    """ Display licenses """
    status = PASS
    text = load_text_resource("LICENSE")
    if text is not None:
        print(text)
    else:
        status = FAIL
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
        status = FAIL
    print("")
    print("Pygments - http://pygments.org/")
    text = load_text_resource("pygments", "LICENSE")
    if text is not None:
        print(text)
    else:
        status = FAIL
    return status


class Convert(object):
    def __init__(
        self, config,
        output=None, basepath=None,
        title=None, settings_path=None
    ):
        self.config = config
        self.output = output
        self.basepath = basepath
        self.title = title
        self.settings_path = settings_path

    def strip_frontmatter(self, text):
        """
        Extract settings from file frontmatter and config file
        Fronmatter options will overwrite config file options.
        """

        frontmatter, text = get_frontmatter_string(text)
        return frontmatter, text

    def get_file_settings(self, file_name, frontmatter={}):
        """
        Using the filename and/or frontmatter, this retrieves
        the full set of settings for this specific file.
        """

        status = PASS
        try:
            self.settings = self.config.get(
                file_name, basepath=self.basepath, output=self.output, frontmatter=frontmatter
            )
        except:
            Logger.log(traceback.format_exc())
            status = FAIL
        return status

    def read_file(self, file_name):
        """ Read the source file """
        try:
            with codecs.open(file_name, "r", encoding=self.config.encoding) as f:
                text = f.read()
        except:
            Logger.log("Failed to open %s!" % file_name)
            text = None
        return text

    def critic_dump(self, file_name, text):
        """ Dump the markdown back out after stripping critic marks """
        status = PASS

        status = self.get_file_settings(file_name)

        if status == PASS and file_name is not None:
            text = self.read_file(file_name)
            if text is None:
                status = FAIL

        if status == PASS:
            if not (self.config.critic & (cd.CRITIC_REJECT | cd.CRITIC_ACCEPT)):
                Logger.log("Acceptance or rejection was not specified for critic dump!")
                status = FAIL
            else:
                # Create text object
                try:
                    txt = formatter.Text(self.settings["builtin"]["destination"], self.config.encoding)
                except:
                    Logger.log("Failed to create text file!")
                    status = FAIL

        if status == PASS:
            text = cd.CriticDump().dump(text, self.config.critic & cd.CRITIC_ACCEPT)
            txt.write(text)
            txt.close()

        return status

    def html_dump(self, file_name, text):
        """ Convet markdown to HTML """
        status = PASS

        html_title = get_title(file_name, self.title)

        if status == PASS and file_name is not None:
            text = self.read_file(file_name)
            if text is None:
                status = FAIL

        if status == PASS:
            frontmatter, text = self.strip_frontmatter(text)
            status = self.get_file_settings(file_name, frontmatter=frontmatter)

        if status == PASS:
            for ref in self.settings["builtin"].get("references", []):
                text += get_references(ref, self.config.encoding)

            # Create html object
            try:
                html = formatter.Html(
                    self.settings["builtin"]["destination"], preview=self.config.preview,
                    plain=self.config.plain, settings=self.settings["settings"],
                    noclasses=self.config.pygments_noclasses
                )
            except:
                Logger.log(traceback.format_exc())
                status = FAIL

        if status == PASS:
            # Convert markdown to HTML
            try:
                mdown = Mdowns(
                    text,
                    base_path=self.settings["builtin"]["basepath"],
                    extensions=self.settings["extensions"]
                )
            except:
                Logger.log(str(traceback.format_exc()))
                html.close()
                status = FAIL

        if status == PASS:
            # Retrieve meta data if available and merge with frontmatter
            # meta data.
            #     1. Frontmatter will override normal meta data.
            #     2. Meta data overrides --title option on command line.
            html.set_meta(
                merge_meta(mdown.meta, self.settings["meta"], title=html_title)
            )

            # Write the markdown
            html.write(mdown.markdown)

            html.close()
            if html.file.name is not None and self.config.preview and status == PASS:
                auto_open(html.file.name)
        return status

    def convert(self, files):
        """ Convert markdown file(s) """
        status = PASS

        # Make sure we have something we can process
        if files is None or len(files) == 0 or files[0] in ('', None):
            Logger.log("Nothing to parse!")
            status = FAIL

        if status == PASS:
            for md_file in files:
                # Quit dumping if there was an error
                if status != PASS:
                    break

                if self.config.is_stream:
                    Logger.log("Converting buffer...")
                else:
                    Logger.log("Converting %s..." % md_file)

                if status == PASS:
                    file_name = md_file if not self.config.is_stream else None
                    text = None if not self.config.is_stream else md_file
                    md_file = None
                    if self.config.critic & cd.CRITIC_DUMP:
                        status = self.critic_dump(file_name, text)
                    else:
                        status = self.html_dump(file_name, text)
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
        parser.add_argument('--output', '-o', nargs=1, default=None, help="Output file. Ignored in batch mode.")
        parser.add_argument('--batch', '-b', action='store_true', default=False, help="Batch mode output.")
        # Input configuration
        parser.add_argument('--settings', '-s', nargs=1, default=[join(script_path, "mdown.json")], help="Load the settings file from an alternate location.")
        parser.add_argument('--encoding', '-e', nargs=1, default=["utf-8"], help="Encoding for input.")
        parser.add_argument('--basepath', nargs=1, default=None, help="The basepath location mdown should use.")
        parser.add_argument('markdown', nargs='*', default=[], help="Markdown file(s) or file pattern(s).")

        args = parser.parse_args()

        if args.licenses:
            return display_licenses()

        Logger.quiet = args.quiet

        files, stream = get_sources(args)
        if stream:
            batch = False
        else:
            batch = args.batch

        if not batch and len(files) > 1:
            Logger.log("Please use batch mode to process multiple files!")
            return FAIL

        config = Settings(
            encoding=args.encoding[0],
            critic=get_critic_mode(args),
            batch=batch,
            stream=stream,
            preview=args.preview,
            settings_path=first_or_none(args.settings),
            plain=args.plain_html
        )

        return Convert(
            basepath=first_or_none(args.basepath),
            title=first_or_none(args.title),
            output=first_or_none(args.output),
            config=config
        ).convert(files)

    script_path = dirname(abspath(sys.argv[0]))
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
else:
    script_path = dirname(abspath(__file__))
