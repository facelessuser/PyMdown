"""
PyMdown Settings.

Manage Settings

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

# Egg resoures must be loaded before Pygments gets loaded
from . import util
util.load_egg_resources()

import codecs
import os.path as path
from . import critic_dump
from . import logger
from . import formatter
from . import mdconvert
from . import settings
import traceback

version_info = (0, 8, 0)

PASS = 0
FAIL = 1


class Convert(object):

    """Converts markdown files."""

    def __init__(self, **kwargs):
        """Unpack user files and then load up settings."""

        util.unpack_user_files()
        self.config = settings.Settings(**kwargs)
        self.config.read_settings()
        self.output = kwargs.get('output')
        self.basepath = kwargs.get('basepath')
        self.relpath = kwargs.get('relpath')
        self.title = kwargs.get('title')
        self.settings_path = kwargs.get('settings_path')

    def merge_meta(self, md_meta, file_name):
        """
        Retrieve Markdown meta data if available and merge frontmatter with it.

            1. Frontmatter will override normal meta data.
            2. Meta data overrides --title option on command line.
        """

        # Resolve title for meta
        if self.title is not None:
            title = str(self.title)
        elif file_name is not None:
            title = path.splitext(path.basename(path.abspath(file_name)))[0]
        else:
            title = None

        # Merge the meta data
        meta = md_meta.copy()
        meta.update(self.settings["page"]["meta"])
        if "title" not in meta and title is not None:
            if title is not None:
                meta["title"] = title
        return meta

    def strip_frontmatter(self, text):
        """
        Extract settings from file frontmatter and config file.

        Fronmatter options will overwrite config file options.
        """

        frontmatter, text = util.get_frontmatter(text)
        return frontmatter, text

    def get_file_settings(self, file_name, frontmatter={}):
        """
        Get the file settings merged with the file's frontmatter.

        Using the filename and/or frontmatter, this retrieves
        the full set of settings for this specific file.
        """

        status = PASS
        try:
            self.settings = self.config.get(
                file_name, output=self.output, basepath=self.basepath,
                relpath=self.relpath, frontmatter=frontmatter
            )
        except:
            logger.Log.error(traceback.format_exc())
            status = FAIL
        return status

    def read_file(self, file_name):
        """Read the source file."""

        try:
            with codecs.open(file_name, "r", encoding=self.config.encoding) as f:
                text = f.read()
        except:
            logger.Log.error("Failed to open %s!" % file_name)
            text = None
        return text

    def critic_dump(self, file_name, text):
        """Dump the markdown back out after stripping critic marks."""

        status = PASS

        status = self.get_file_settings(file_name)
        is_valid_dump = not (
            self.config.critic &
            (util.CRITIC_REJECT | util.CRITIC_ACCEPT)
        )

        if status == PASS and file_name is not None:
            text = self.read_file(file_name)
            if text is None:
                status = FAIL

        if status == PASS and is_valid_dump:
            logger.Log.error("Acceptance or rejection was not specified for critic dump!")
            status = FAIL

        if status == PASS:
            txt = formatter.Text(self.config.output_encoding)

            # Create text object
            try:
                txt.open(self.settings["page"]["destination"])
                # Apply critic stripping
                text = critic_dump.CriticDump().dump(
                    text,
                    self.config.critic & util.CRITIC_ACCEPT,
                    self.config.critic & util.CRITIC_VIEW
                )

                # Dump the converted text
                txt.write(text)
            except:
                logger.Log.error(str(traceback.format_exc()))
                status = FAIL

            # Close up the text file
            txt.close()

        return status

    def html_dump(self, file_name, text):
        """Convet markdown to HTML."""

        status = PASS

        if status == PASS and file_name is not None:
            text = self.read_file(file_name)
            if text is None:
                status = FAIL

        if status == PASS:
            frontmatter, text = self.strip_frontmatter(text)
            status = self.get_file_settings(file_name, frontmatter=frontmatter)

        if status == PASS:
            # Append Markdown reference files to current Markdown content
            text += util.get_references(
                self.settings["page"].get("references", []),
                self.settings["page"]["basepath"],
                self.config.encoding
            )

            # Create html object
            html = formatter.Html(
                preview=self.config.preview,
                plain=self.config.plain,
                settings=self.settings["settings"],
                basepath=self.settings["page"]["basepath"],
                relative=self.settings["page"]["relpath"],
                aliases=self.settings["page"]["include"],
                encoding=self.config.output_encoding
            )
            try:
                html.open(self.settings["page"]["destination"])

                # Set up Converter
                converter = mdconvert.MdConverts(
                    text,
                    smart_emphasis=self.settings["settings"].get('smart_emphasis', True),
                    lazy_ol=self.settings["settings"].get('lazy_ol', True),
                    tab_length=self.settings["settings"].get('tab_length', 4),
                    base_path=self.settings["page"]["basepath"],
                    relative_path=self.settings["page"]["relpath"],
                    output_path=path.dirname(html.file.name) if html.file.name else self.config.out,
                    enable_attributes=self.settings["settings"].get('enable_attributes', True),
                    output_format=self.settings["settings"].get('output_format', 'xhtml1'),
                    extensions=self.settings["settings"]["extensions"]
                )

                # Markdown -> HTML
                converter.convert()

                # Merge meta data
                html.set_meta(self.merge_meta(converter.meta, file_name))

                # Write the markdown to the HTML
                html.write_header()
                html.write(converter.markdown)
                html.write_footer()
            except:
                logger.Log.error(str(traceback.format_exc()))
                status = FAIL

            # Close the HTML file
            html.close()

        # Preview the markdown
        if status == PASS and html.file.name is not None and self.config.preview:
            util.open_in_browser(html.file.name)
        return status

    def convert(self, files):
        """Convert markdown file(s)."""

        status = PASS

        # Make sure we have something we can process
        if files is None or len(files) == 0 or files[0] in ('', None):
            logger.Log.error("Nothing to parse!")
            status = FAIL

        if status == PASS:
            for md_file in files:
                # Quit dumping if there was an error
                if status != PASS:
                    break

                if self.config.is_stream:
                    logger.Log.info("Converting buffer...")
                else:
                    logger.Log.info("Converting %s..." % md_file)

                if status == PASS:
                    file_name = md_file if not self.config.is_stream else None
                    text = None if not self.config.is_stream else md_file
                    md_file = None
                    if self.config.critic & util.CRITIC_DUMP:
                        status = self.critic_dump(file_name, text)
                    else:
                        status = self.html_dump(file_name, text)
        return status
