import json
import re
import codecs
import yaml
from .logger import Logger
import traceback


def get_frontmatter(source, encoding):
    with codecs.open(source, "r", encoding=encoding) as f:
        return get_frontmatter_string(f.read())
    return None, None


def get_frontmatter_string(string):
    frontmatter = {}

    if string.startswith("---"):
        m = re.search(r'^(---(.*?)---\r?\n)', string, re.DOTALL)
        if m:
            try:
                frontmatter = json.loads(m.group(2))
            except:
                try:
                    frontmatter = yaml.load(m.group(2))
                except:
                    Logger.log(traceback.format_exc())
                    pass
            string = string[m.end(1):]

    return frontmatter, string
