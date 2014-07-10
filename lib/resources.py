from __future__ import unicode_literals
from __future__ import print_function
import sys
from os.path import join, exists, abspath, dirname
import codecs

RESOURCE_PATH = abspath(join(dirname(__file__), ".."))


def load_text_resource(*args):
    base = None
    try:
        base = sys._MEIPASS
    except:
        base = RESOURCE_PATH

    path = join(base, *args)

    data = None
    if exists(path):
        try:
            with codecs.open(path, "rb") as f:
                data = f.read().decode("utf-8")
        except:
            # print(traceback.format_exc())
            pass
    return data