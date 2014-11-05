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
from __future__ import absolute_import
from __future__ import print_function
# Egg resoures must be loaded before Pygments gets loaded
from lib.resources import load_text_resource, load_egg_resources, splitenc, get_user_path
load_egg_resources()
import codecs
import sys
import subprocess
import webbrowser
import traceback
import json
from os.path import dirname, abspath, normpath, exists, basename, join, isfile, expanduser, splitext
from lib.logger import Logger, INFO, CRITICAL, DEBUG
from lib.settings import Settings
from lib.settings import CRITIC_IGNORE, CRITIC_ACCEPT, CRITIC_REJECT, CRITIC_DUMP, CRITIC_VIEW
import lib.critic_dump as critic_dump
from lib.mdconvert import MdConverts
from lib import formatter
from lib.frontmatter import get_frontmatter_string
try:
    from lib import scrub
    scrublib = True
except:
    scrublib = False

__version_info__ = (0, 7, 0)
__version__ = '.'.join(map(str, __version_info__))

PY3 = sys.version_info >= (3, 0)

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

PASS = 0
FAIL = 1

script_path = dirname(abspath(__file__))


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
        all_files.add(abspath(normpath(f)))
    return list(all_files)


def get_file_stream(encoding):
    """ Get the file stream """

    import fileinput
    import traceback
    sys.argv = []
    text = []
    try:
        for line in fileinput.input():
            text.append(line if PY3 else line.decode(encoding))
        stream = ''.join(text)
    except:
        Logger.error(traceback.format_exc())
        stream = None
    text = None
    return stream


def open_with_osx_browser(filename):
    """ Open file with browser id """
    web_handler = None
    launch_services = expanduser('~/Library/Preferences/com.apple.LaunchServices.plist')
    with open(launch_services, "rb") as f:
        content = f.read()
    args = ["plutil", "-convert", "json", "-o", "-", "--", "-"]
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(content)
    out, err = p.communicate()
    plist = json.loads(out.decode('utf-8') if PY3 else out)
    for handler in plist['LSHandlers']:
        if handler.get('LSHandlerURLScheme', '') == "http":
            web_handler = handler.get('LSHandlerRoleAll', None)
    if web_handler is not None:
        subprocess.Popen(['open', '-b', web_handler, filename])


def auto_open(name):
    """ Auto open HTML """

    # Here is an attempt to load the HTML in the
    # the default browser.  I guess if this doesn't work
    # I could always just inlcude the desktop lib.
    if _PLATFORM == "osx":
        try:
            open_with_osx_browser(name)
        except:
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
    critic_mode = CRITIC_IGNORE
    if args.accept and args.reject:
        critic_mode |= CRITIC_VIEW
    elif args.accept:
        critic_mode |= CRITIC_ACCEPT
    elif args.reject:
        critic_mode |= CRITIC_REJECT
    if args.critic_dump:
        critic_mode |= CRITIC_DUMP
    return critic_mode


def get_references(references, encoding):
    """ Get footnote and general references from outside source """
    text = ''
    for file_name in references:
        file_name, encoding = splitenc(file_name, default=encoding)
        user_path = join(get_user_path(), file_name)
        if file_name is not None:
            if exists(file_name) and isfile(file_name):
                text += load_text_resource(file_name, encoding=encoding)
            elif exists(user_path) and isfile(user_path):
                text += load_text_resource(user_path, encoding=encoding)
            else:
                Logger.error("Could not find reference file %s!" % file_name)
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
        title = splitext(basename(abspath(file_name)))[0]
    else:
        title = None
    return title


def merge_meta(meta1, meta2, title=None):
    """ Merge meta1 and meta2.  Add title to meta data if needed. """
    meta = meta1.copy()
    meta.update(meta2)
    if "title" not in meta and title is not None:
        if title is not None:
            meta["title"] = title
    return meta


def display_licenses():
    """ Display licenses """
    status = PASS
    text = load_text_resource(join('data', 'licenses.txt'), internal=True)
    if text is not None:
        if PY3:
            sys.stdout.buffer.write(text.encode('utf-8'))
        else:
            sys.stdout.write(text.encode('utf-8'))
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
            Logger.error(traceback.format_exc())
            status = FAIL
        return status

    def read_file(self, file_name):
        """ Read the source file """
        try:
            with codecs.open(file_name, "r", encoding=self.config.encoding) as f:
                text = f.read()
        except:
            Logger.error("Failed to open %s!" % file_name)
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
            if not (self.config.critic & (CRITIC_REJECT | CRITIC_ACCEPT)):
                Logger.error("Acceptance or rejection was not specified for critic dump!")
                status = FAIL
            else:
                # Create text object
                try:
                    txt = formatter.Text(self.settings["page"]["destination"], self.config.output_encoding)
                except:
                    Logger.error("Failed to create text file!")
                    status = FAIL

        if status == PASS:
            text = critic_dump.CriticDump().dump(
                text,
                self.config.critic & CRITIC_ACCEPT,
                self.config.critic & CRITIC_VIEW
            )
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
            text += get_references(self.settings["page"].get("references", []), self.config.encoding)

            # Create html object
            try:
                html = formatter.Html(
                    self.settings["page"]["destination"], preview=self.config.preview,
                    plain=self.config.plain, settings=self.settings["settings"],
                    basepath=self.settings["page"]["basepath"],
                    aliases=self.settings["page"]["include"],
                    encoding=self.config.output_encoding
                )
            except:
                Logger.error(traceback.format_exc())
                status = FAIL

        if status == PASS:
            # Convert markdown to HTML
            try:
                if html.file.name:
                    destination = dirname(html.file.name)
                elif self.config.destination:
                    destination = dirname(self.config.destination)
                else:
                    destination = None
                converter = MdConverts(
                    text,
                    smart_emphasis=self.settings["settings"].get('smart_emphasis', True),
                    lazy_ol=self.settings["settings"].get('lazy_ol', True),
                    tab_length=self.settings["settings"].get('tab_length', 4),
                    base_path=self.settings["page"]["basepath"],
                    destination=destination,
                    enable_attributes=self.settings["settings"].get('enable_attributes', True),
                    output_format=self.settings["settings"].get('output_format', 'xhtml1'),
                    extensions=self.settings["settings"]["extensions"]
                )

                # Retrieve meta data if available and merge with frontmatter
                # meta data.
                #     1. Frontmatter will override normal meta data.
                #     2. Meta data overrides --title option on command line.
                html.set_meta(
                    merge_meta(converter.meta, self.settings["meta"], title=html_title)
                )
            except:
                Logger.error(str(traceback.format_exc()))
                html.close()
                status = FAIL

        if status == PASS:
            # Write the markdown
            html.write(scrub.scrub(converter.markdown) if self.config.clean else converter.markdown)
            html.close()

            # Preview the markdown
            if html.file.name is not None and self.config.preview and status == PASS:
                auto_open(html.file.name)
        return status

    def convert(self, files):
        """ Convert markdown file(s) """
        status = PASS

        # Make sure we have something we can process
        if files is None or len(files) == 0 or files[0] in ('', None):
            Logger.error("Nothing to parse!")
            status = FAIL

        if status == PASS:
            for md_file in files:
                # Quit dumping if there was an error
                if status != PASS:
                    break

                if self.config.is_stream:
                    Logger.info("Converting buffer...")
                else:
                    Logger.info("Converting %s..." % md_file)

                if status == PASS:
                    file_name = md_file if not self.config.is_stream else None
                    text = None if not self.config.is_stream else md_file
                    md_file = None
                    if self.config.critic & CRITIC_DUMP:
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

        parser = argparse.ArgumentParser(prog='pymdown', description='Markdown generator')
        # Flag arguments
        parser.add_argument('--version', action='version', version="%(prog)s " + __version__)
        parser.add_argument('--debug', '-d', action='store_true', default=False, help=argparse.SUPPRESS)
        parser.add_argument('--licenses', action='store_true', default=False, help="Display licenses.")
        parser.add_argument('--quiet', '-q', action='store_true', default=False, help="No messages on stdout.")
        # Format and Viewing
        parser.add_argument('--preview', '-p', action='store_true', default=False, help="Output to preview (temp file). --output will be ignored.")
        parser.add_argument('--plain-html', '-P', action='store_true', default=False, help="Strip out CSS, style, ids, etc.  Just show tags.")
        parser.add_argument('--title', nargs=1, default=None, help="Title for HTML.")
        # Critic features
        parser.add_argument('--accept', '-a', action='store_true', default=False, help="Accept propossed critic marks when using in normal processing and --critic-dump processing")
        parser.add_argument('--reject', '-r', action='store_true', default=False, help="Reject propossed critic marks when using in normal processing and --critic-dump processing")
        parser.add_argument('--critic-dump', action='store_true', default=False, help="Process critic marks, dumps file(s), and exits.")
        # Output
        parser.add_argument('--output', '-o', nargs=1, default=None, help="Output file. Ignored in batch mode.")
        parser.add_argument('--batch', '-b', action='store_true', default=False, help="Batch mode output.")
        parser.add_argument('--force-stdout', action='store_true', default=False, help="Force output to stdout.")
        parser.add_argument('--force-no-template', action='store_true', default=False, help="Force using no template.")
        parser.add_argument('--output-encoding', '-E', nargs=1, default=[None], help="Output encoding.")
        parser.add_argument('--clean', '-c', action='store_true', default=False, help=argparse.SUPPRESS)
        # Input configuration
        parser.add_argument('--settings', '-s', nargs=1, default=[join(get_user_path(), "pymdown.cfg")], help="Load the settings file from an alternate location.")
        parser.add_argument('--encoding', '-e', nargs=1, default=["utf-8"], help="Encoding for input.")
        parser.add_argument('--basepath', nargs=1, default=None, help="The basepath location pymdown should use.")
        parser.add_argument('markdown', nargs='*', default=[], help="Markdown file(s) or file pattern(s).")

        args = parser.parse_args()

        if args.licenses:
            return display_licenses()

        if args.debug:
            Logger.set_level(CRITICAL if args.quiet else DEBUG)
        else:
            Logger.set_level(CRITICAL if args.quiet else INFO)

        files, stream = get_sources(args)
        if stream:
            batch = False
        else:
            batch = args.batch

        if not batch and len(files) > 1:
            Logger.log("Please use batch mode to process multiple files!")
            return FAIL

        # It is assumed that the input encoding is desired for output
        # unless otherwise specified.
        if args.output_encoding[0] is None:
            args.output_encoding[0] = args.encoding[0]

        # Setup config class
        config = Settings(
            encoding=args.encoding[0],
            output_encoding=args.output_encoding[0],
            critic=get_critic_mode(args),
            batch=batch,
            stream=stream,
            preview=args.preview,
            settings_path=first_or_none(args.settings),
            plain=args.plain_html,
            force_stdout=args.force_stdout,
            force_no_template=args.force_no_template,
            clean=(args.clean if scrublib else False)
        )

        # Convert
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
