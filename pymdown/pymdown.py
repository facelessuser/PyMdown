from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

# Egg resoures must be loaded before Pygments gets loaded
from . import resources as res
res.load_egg_resources()

import codecs
import os.path as path
from . import critic_dump
from . import logger
from . import formatter
from . import mdconvert
from . import settings
from . frontmatter import get_frontmatter_string
from .util import open_in_browser
import traceback
try:
    from lib import scrub
    SCRUB_AVAILABLE = True
except:
    SCRUB_AVAILABLE = False

version_info = (0, 8, 0)

PASS = 0
FAIL = 1


def get_references(references, basepath, encoding):
    """ Get footnote and general references from outside source """

    text = ''
    for file_name in references:
        file_name, encoding = res.splitenc(file_name, default=encoding)
        user_path = path.join(res.get_user_path(), file_name)

        is_abs = res.is_absolute(file_name)

        # Find path relative to basepath or global user path
        # If basepath is defined set paths relative to the basepath if possible
        # or just keep the absolute
        if not is_abs:
            # Is relative path
            base_temp = path.normpath(path.join(basepath, file_name)) if basepath is not None else None
            user_temp = path.normpath(path.join(user_path, file_name)) if user_path is not None else None
            if base_temp is not None and path.exists(base_temp) and path.isfile(base_temp):
                ref_path = base_temp
            elif user_temp is not None and path.exists(user_temp) and path.isfile(user_temp):
                ref_path = user_temp
            else:
                # Is an unknown path
                ref_path = None
        elif is_abs and path.exists(file_name) and path.isfile(file_name):
            # Is absolute path
            ref_path = file_name
        else:
            # Is an unknown path
            ref_path = None

        if ref_path is not None:
            text += res.load_text_resource(ref_path, encoding=encoding)
        else:
            logger.Log.error("Could not find reference file %s!" % file_name)
    return text


def get_title(file_name, title_val):
    """ Get title for HTML """
    if title_val is not None:
        title = str(title_val)
    elif file_name is not None:
        title = path.splitext(path.basename(path.abspath(file_name)))[0]
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


class Convert(object):
    def __init__(
        self, config,
        output=None, basepath=None, relpath=None,
        title=None, settings_path=None
    ):
        self.config = config
        self.output = output
        self.basepath = basepath
        self.relpath = relpath
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
                file_name, output=self.output, basepath=self.basepath,
                relpath=self.relpath, frontmatter=frontmatter
            )
        except:
            logger.Log.error(traceback.format_exc())
            status = FAIL
        return status

    def read_file(self, file_name):
        """ Read the source file """
        try:
            with codecs.open(file_name, "r", encoding=self.config.encoding) as f:
                text = f.read()
        except:
            logger.Log.error("Failed to open %s!" % file_name)
            text = None
        return text

    def critic_dump(self, file_name, text):
        """ Dump the markdown back out after stripping critic marks """
        status = PASS

        status = self.get_file_settings(file_name)
        is_valid_dump = not (
            self.config.critic &
            (settings.CRITIC_REJECT | settings.CRITIC_ACCEPT)
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
                    self.config.critic & settings.CRITIC_ACCEPT,
                    self.config.critic & settings.CRITIC_VIEW
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
        """ Convet markdown to HTML """
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
            text += get_references(
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

                # Retrieve meta data if available and merge with frontmatter
                # meta data.
                #     1. Frontmatter will override normal meta data.
                #     2. Meta data overrides --title option on command line.
                html.set_meta(
                    merge_meta(
                        converter.meta,
                        self.settings["page"]["meta"],
                        title=get_title(file_name, self.title)
                    )
                )

                # Experimental content scrubbing
                can_scrub = self.config.clean and SCRUB_AVAILABLE
                content = scrub.scrub(converter.markdown) if can_scrub else converter.markdown

                # Write the markdown to the HTML
                html.write_header()
                html.write(content)
                html.write_footer()
            except:
                logger.Log.error(str(traceback.format_exc()))
                status = FAIL

            # Close the HTML file
            html.close()

        # Preview the markdown
        if status == PASS and html.file.name is not None and self.config.preview:
            open_in_browser(html.file.name)
        return status

    def convert(self, files):
        """ Convert markdown file(s) """
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
                    if self.config.critic & settings.CRITIC_DUMP:
                        status = self.critic_dump(file_name, text)
                    else:
                        status = self.html_dump(file_name, text)
        return status
