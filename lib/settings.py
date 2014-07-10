from . import critic_dump as cd
from os.path import dirname, abspath, exists
import codecs
from os.path import isfile, isdir, splitext, join, basename
from . import resources as res
import traceback
from .logger import Logger
import json
import re
from .file_strip.json import sanitize_json
from copy import deepcopy

BUILTIN_KEYS = ('title', 'destination', 'basepath', 'references')


class MdownSettingsException(Exception):
    pass


class Settings(object):
    def __init__(
        self, settings_path=None, stream=False,
        batch=False, critic=cd.CRITIC_IGNORE,
        plain=False, preview=False, encoding='utf-8'
    ):
        self.critic = critic
        self.plain = plain
        self.batch = batch
        self.encoding = encoding
        self.preview = preview
        self.is_stream = stream
        self.settings = {
            "builtin": {
                "title": None,
                "destination": None,
                "basepath": None,
                "references": None
            },
            "settings": {},
            "other": {}
        }

        # Use default file if one was not provided
        if settings_path is None or not exists(settings_path):
            settings_path = join(res.RESOURCE_PATH, "mdown.json")

        # Get the settings if available
        self.read_settings(settings_path)

    def read_settings(self, settings_path):
        """
        Get the settings and add absolutepath
        extention if a preview is planned.
        Unpack the settings file if needed.
        """

        # Unpack default settings file if needed
        if not exists(settings_path):
            text = res.load_text_resource("mdown.json")
            try:
                with codecs.open(settings_path, "w", encoding="utf-8") as f:
                    f.write(text)
            except:
                Logger.log(traceback.format_exc())

        # Try and read settings file
        settings = {}
        try:
            with open(settings_path, "r") as f:
                settings = json.loads(sanitize_json(f.read()))
        except:
            Logger.log(traceback.format_exc())
            raise MdownSettingsException("Could not parse settings file!")

        self.settings["settings"] = settings

    def get(self, file_name, output, title, basepath, frontmatter=None):
        self.file_name = file_name
        settings = deepcopy(self.settings)
        settings["builtin"]["title"] = self.get_title(title)
        settings["builtin"]["destination"] = self.get_output(output)
        settings["builtin"]["basepath"] = self.get_base_path(basepath)
        if frontmatter is not None:
            self.apply_frontmatter(frontmatter, settings)
        self.post_process_settings(settings)
        return settings

    def apply_frontmatter(self, frontmatter, settings):
        for key, value in frontmatter.items():
            if key in ("settings") and isinstance(value, dict):
                for subkey, subvalue in value.items():
                    settings[key][subkey] = subvalue
            elif key in BUILTIN_KEYS:
                if key == "basepath" and not self.batch:
                    settings["builtin"][key] = self.get_base_path(value)
                elif key == "destination":
                    settings["builtin"][key] = self.get_output(value)
                elif key == "references":
                    settings["builtin"][key] = value if exists(value) else None
                else:
                    settings["builtin"][key] = value
            else:
                settings["other"][key] = value

    def get_output(self, out_name):
        """
        Get the path to output the file.
        """

        critic_enabled = self.critic & cd.CRITIC_ACCEPT or self.critic & cd.CRITIC_REJECT
        output = None
        if not self.batch:
            if out_name is not None:
                name = abspath(out_name)
                if isdir(out_name):
                    Logger.log("'%s' is a directory!" % name)
                elif exists(dirname(name)):
                    output = name
                else:
                    Logger.log("'%s' directory does not exist!" % name)
        else:
            name = abspath(self.file_name)
            if self.critic & cd.CRITIC_DUMP and critic_enabled:
                if self.critic & cd.CRITIC_REJECT:
                    label = ".rejected"
                else:
                    label = ".accepted"
                base, ext = splitext(abspath(self.file_name))
                output = join(name, "%s%s%s" % (base, label, ext))
            else:
                output = join(name, "%s.html" % splitext(abspath(self.file_name))[0])

        return output

    def get_title(self, title_val):
        """ Get title for HTML """
        if title_val is not None:
            title = title_val
        elif not self.is_stream:
            title = basename(abspath(self.file_name))
        else:
            title = None
        return title

    def get_base_path(self, basepath):
        """ Get the base path to use when resolving basepath paths if possible """

        if basepath is not None and exists(basepath):
            # A valid path was fed in
            path = basepath
            basepath = dirname(abspath(path)) if isfile(path) else abspath(path)
        elif not self.is_stream:
            # Use the current file path
            basepath = dirname(abspath(self.file_name))
        else:
            # Okay, there is no way to tell the orign.
            # We are probably a stream that has no specified
            # physical location.
            basepath = None

        return basepath

    def post_process_settings(self, settings):
        absolute = False
        critic_found = []
        plain_html = []
        if "extensions" in settings["settings"]:
            extensions = deepcopy(settings["settings"].get("extensions", []))
            del settings["settings"]["extensions"]

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

        # Ensure the user can never set plainhtml mode directly
        for index in reversed(plain_html):
            del extensions[index]

        # Ensure previews are using absolute paths
        if self.preview and not absolute:
            extensions.append("mdownx.absolutepath(base_path=${BASE_PATH})")

        # Handle the appropriate critic mode internally
        # Critic must be appended to end of extension list
        if self.critic != cd.CRITIC_OFF:
            mode = "ignore"
            if self.critic & cd.CRITIC_ACCEPT:
                mode = "accept"
            elif self.critic & cd.CRITIC_REJECT:
                mode = "reject"
            extensions.append("mdownx.critic(mode=%s)" % mode)

        # Handle plainhtml internally.  Must be appended to the end. Okay to come after critic.
        if self.plain:
            extensions.append("mdownx.plainhtml")

        settings["extensions"] = extensions

        # Find the style
        style = None
        re_pygment = r"pygments_style\s*=\s*([a-zA-Z][a-zA-Z_\d]*)"
        for e in extensions:
            if e.startswith("codehilite"):
                pygment_style = re.search(re_pygment, e)
                style = "default" if pygment_style is None else pygment_style.group(1)
        settings["settings"]["style"] = style
