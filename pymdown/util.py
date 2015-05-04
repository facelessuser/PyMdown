import yaml
import json
import webbrowser
import subprocess
from collections import OrderedDict
from .compat import PLATFORM, to_unicode
from os import path

__all__ = ["reduce_list", "yaml_load", "open_in_browser"]


def yaml_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Make all YAML dictionaries load as ordered Dicts.
    http://stackoverflow.com/a/21912744/3609487
    """
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping
    )

    return yaml.load(stream, OrderedLoader)


def reduce_list(data_set):
    """ Reduce duplicate items in a list and preserve order """
    seen = set()
    return [item for item in data_set if item not in seen and not seen.add(item)]


def open_in_browser(name):
    """ Auto open HTML """

    # Here is an attempt to load the HTML in the
    # the default browser.  I guess if this doesn't work
    # I could always just inlcude the desktop lib.
    if PLATFORM == "osx":
        web_handler = None
        try:
            launch_services = path.expanduser('~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist')
            if not path.exists(launch_services):
                launch_services = path.expanduser('~/Library/Preferences/com.apple.LaunchServices.plist')
            with open(launch_services, "rb") as f:
                content = f.read()
            args = ["plutil", "-convert", "json", "-o", "-", "--", "-"]
            p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            p.stdin.write(content)
            out, err = p.communicate()
            plist = json.loads(to_unicode(out))
            for handler in plist['LSHandlers']:
                print('found')
                if handler.get('LSHandlerURLScheme', '') == "http":
                    web_handler = handler.get('LSHandlerRoleAll', None)
                    break
        except:
            pass
        if web_handler is not None:
            subprocess.Popen(['open', '-b', web_handler, name])
        else:
            subprocess.Popen(['open', name])
    elif PLATFORM == "windows":
        webbrowser.open(name, new=2)
    else:
        try:
            # Maybe...?
            subprocess.Popen(['xdg-open', name])
        except OSError:
            webbrowser.open(name, new=2)
            # Well we gave it our best...
