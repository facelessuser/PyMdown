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
from os.path import dirname, abspath, normpath, exists
from lib.logger import Logger
from lib import critic_dump as cd
from lib.settings import Settings
from lib.resources import load_text_resource
from lib.mdown import Mdowns
from lib import formatter
from lib.frontmatter import get_frontmatter_string, get_frontmatter

__version_info__ = (0, 3, 1)
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
    text = ''
    if file_name is not None and exists(file_name):
        try:
            with codecs.open(file_name, "r", encoding=encoding) as f:
                text = f.read()
        except:
            Logger.log(traceback.format_exc())
    return text


def get_sources(args):
    # Get file(s) or stream
    files = None
    stream = False

    try:
        files = get_files(args.markdown)
    except:
        files = [get_file_stream(args.encoding[0])]
        stream = True
    return files, stream


def display_licenses():
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


def convert(
    files, config, encoding="utf-8",
    output=None, basepath=None,
    title=None, settings_path=None
):
    """ Convert markdown file(s) to html """
    status = PASS

    # Make sure we have something we can process
    if files is None or len(files) == 0 or files[0] in ('', None):
        Logger.log("Nothing to parse!")
        status = FAIL

    output_stream = None

    if status == PASS:
        total_files = len(files)
        for count in range(0, total_files):
            md_file = files[count]

            # Quit dumping if there was an error
            if status != PASS:
                break

            if config.is_stream:
                Logger.log("Converting buffer...")
            else:
                Logger.log("Converting %s..." % md_file)

            try:
                # Extract settings from file frontmatter and config file
                # Fronmatter options will overwrite config file options.
                if not config.is_stream:
                    frontmatter, text = get_frontmatter(md_file, config.encoding)
                else:
                    frontmatter, text = get_frontmatter_string(md_file)
                settings = config.get(
                    md_file, basepath=basepath, title=title, output=output, frontmatter=frontmatter
                )
            except:
                Logger.log(traceback.format_exc())
                status = FAIL

            if status == PASS:
                if config.critic & cd.CRITIC_DUMP:
                    if not (config.critic & cd.CRITIC_REJECT or config.critic & cd.CRITIC_ACCEPT):
                        Logger.log("Acceptance or rejection was not specified for critic dump!")
                        status = FAIL
                    else:
                        if config.batch or (count == 0 and not config.batch):
                            try:
                                output_stream = formatter.Text(output, encoding)
                            except:
                                status = FAIL
                                break

                        text = cd.CriticDump().dump(text, config.critic & cd.CRITIC_ACCEPT)
                        output_stream.write(text)

                        if (count + 1 == total_files and not config.batch) or config.batch:
                            output_stream.close()
                            output_stream = None
                else:
                    text += get_references(settings["builtin"].get("references"), config.encoding)

                    # Get reference file if specified
                    if config.batch or (count == 0 and not config.batch):
                        try:
                            output_stream = formatter.Html(
                                settings["builtin"]["destination"], preview=config.preview, title=settings["builtin"]["title"],
                                plain=config.plain, settings=settings["settings"], noclasses=config.pygments_noclasses
                            )
                        except:
                            Logger.log(traceback.format_exc())
                            status = FAIL
                            break

                    try:
                        mdown = Mdowns(
                            text,
                            base_path=settings["builtin"]["basepath"],
                            extensions=settings["extensions"]
                        )
                    except:
                        Logger.log(str(traceback.format_exc()))
                        output_stream.close()
                        status = FAIL
                        break

                    output_stream.write(mdown.markdown)

                    if (count + 1 == total_files and not config.batch) or config.batch:
                        output_stream.close()
                        if output_stream.file.name is not None and config.preview and status == PASS:
                            auto_open(output_stream.file.name)
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
        parser.add_argument('--settings', '-s', nargs=1, default=None, help="Load the settings file from an alternate location.")
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

        config = Settings(
            encoding=args.encoding[0],
            critic=get_critic_mode(args),
            batch=batch,
            stream=stream,
            preview=args.preview,
            settings_path=first_or_none(args.settings),
            plain=args.plain_html
        )

        return convert(
            files=files,
            basepath=first_or_none(args.basepath),
            title=first_or_none(args.title),
            output=first_or_none(args.output),
            config=config
        )

    script_path = dirname(abspath(sys.argv[0]))
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
else:
    script_path = dirname(abspath(__file__))
