import sys
# pip install webcolors
from webcolors import name_to_hex, normalize_hex
from os.path import dirname, abspath, join, normpath, exists
import re

support_lib = normpath(join(dirname(abspath(__file__)), ".."))
if exists(support_lib) and support_lib not in sys.path:
    sys.path.append(support_lib)
from lib.file_strip.comments import Comments

HEADER = '''"""
Reverse generated from CSS back to PY via pyg_css_convert.py
"""
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \\
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal


'''

CLASS_START = '''class %sStyle(Style):
    background_color = "%s"  %s
    highlight_color = "%s"   %s

    styles = {
%s
    }
'''

from pygments.token import STANDARD_TYPES as st

prefix = sys.argv[1]
name = sys.argv[2]
css_file = sys.argv[3]
folder = dirname(abspath(css_file))
if folder == "":
    folder == '.'
lname = name.lower()

print(prefix)
print(name)
print(lname)

tokens = {"hll": "highlight_color"}

for k, v in st.items():
    if v == "":
        continue
    tokens[v] = str(k).replace("Token.", '')

RE_STYLES = re.compile(
    r'''
    (?:
        (?P<text>^\s*%(prefix)s\s*\{(?P<t_rule>[^}]+?)\}\s*$)|
        (?P<rule>^\s*%(prefix)s\s*\.(?P<class>\w+)\s*\{(?P<c_rule>[^}]+?)\}\s*$)|
        (?P<other>^\s*[^{]+\{[^}]+?\})|
        (?P<invalid>.)
    )
    ''' % {"prefix": prefix}, re.MULTILINE | re.DOTALL | re.VERBOSE
)


def get_settings(rule):
    obj = {
        "bold": False,
        "italic": False,
        "underline": False,
        "foreground": None,
        "background": None,
        "border": None
    }

    if re.search(r"(?<!-)\bfont-weight\s*:\s*bold", rule) is not None:
        obj["bold"] = True
    if re.search(r"(?<!-)\bfont-style\s*:\s*italic", rule) is not None:
        obj["italic"] = True
    if re.search(r"(?<!-)\btext-decoration\s*:\s*underline", rule) is not None:
        obj["underline"] = True
    m = re.search(r"(?<!-)\bborder\s*:\s*[\d]+px\s*\w+\s*(?P<color>#[a-zA-z\d]{6}|#[a-zA-z\d]{3}|\w+)", rule)
    if m:
        color = m.group('color')
        obj["border"] = normalize_hex(color) if color.startswith('#') else name_to_hex(color)
    m = re.search(r"(?<!-)\bcolor\s*:\s*(?P<color>#[a-zA-z\d]{6}|#[a-zA-z\d]{3}|\w+)", rule)
    if m:
        color = m.group('color')
        obj["foreground"] = normalize_hex(color) if color.startswith('#') else name_to_hex(color)
    m = re.search(r"(?<!-)\bbackground-color\s*:\s*(?P<color>#[a-zA-z\d]{6}|#[a-zA-z\d]{3}|\w+)", rule)
    if m:
        color = m.group('color')
        obj["background"] = normalize_hex(color) if color.startswith('#') else name_to_hex(color)
    return obj


def process(m):
    if m.group('text'):
        obj = get_settings(m.group('t_rule'))
        obj["class"] = "text"
        return obj
    elif m.group('rule'):
        c = m.group('class')
        obj = get_settings(m.group('c_rule'))
        obj["class"] = c
        return obj
    elif m.group('other'):
        return {"class": "other", "rule": m.group(0)}
    else:
        return {"class": "invalid"}


def strip_exclusions(rules):
    count = 0
    total = len(rules)
    for i in range(0, total):
        item = rules[i]
        compare = item[0]
        sub_compare = None
        for attr in ("bold", "italic", "underline"):
            if attr in item[1]:
                for x in range(count + 1, total):
                    sibling = rules[x]
                    if sibling[0].startswith(compare):
                        if sub_compare is not None and sibling[0].startswith(sub_compare):
                            # Ignore children of already negative matched
                            # sub-child
                            pass
                        elif attr not in sibling[1]:
                            # Negative matched sub-child
                            sibling[1].append("no" + attr)
                            sub_compare = sibling[0]
                        else:
                            # Match child inherited
                            sibling[1].remove(attr)
                    else:
                        break
        count += 1


def format_rules(rules, undetected, invalid, max_length):
    strip_exclusions(rules)
    text = ""
    last = len(rules) - 1
    idx = 0
    for r in rules:
        text += ('        %-' + str(max_length + 1) + 's "%s"') % (r[0] + ":", ' '.join(r[1]))
        if idx != last:
            text += ","
            if r[2] != "":
                text += "  %s" % r[2]
            text += "\n"
        elif r[2] != "":
            text += "  %s" % r[2]
        idx += 1
    text += "\n\n        # Below are classes that could not be resolved:"
    for undef in undetected:
        text += (
            "\n        # class=.%(class)s "
            "bold=%(bold)s "
            "italic=%(italic)s "
            "underline=%(underline)s "
            "color=%(foreground)s "
            "bg=%(background)s "
            "border=%(border)s"
        ) % obj
    text += "\n\n        # Below are invalid rules:"
    for inv in invalid:
        text += "\n        # %s" % inv
    return text


with open(css_file, "r") as r:
    text = []
    source = Comments('css', False).strip(r.read())
    m = re.search(r"(^\s*|\}\n*\s*)\s*%s\s*\{(?P<b_rule>[^}]+?)\}\s*" % prefix, source)
    bg = "#ffffff"
    hl = "#ffffcc"
    fg = "#000000"
    hl_comment = "# <-- Not defined; defaulted"
    bg_comment = "# <-- Not defined; defaulted"
    fg_comment = "# <-- Not defined; defaulted"

    undetected = []
    invalid = []
    max_length = 0

    for m in RE_STYLES.finditer(source):
        obj = process(m)
        if obj is None:
            continue

        if obj['class'] in ("other", "invalid"):
            if obj['class'] == "other":
                invalid.append(obj['rule'])
            continue

        if obj['class'] == "text":
            if obj['background'] is not None:
                bg = obj['background']
                bg_comment = '# Background'
            if obj['foreground'] is not None:
                fg = obj['foreground']
                fg_comment = '# Foreground'
            continue

        c = tokens.get(obj['class'], None)
        if c is not None:
            if obj['class'] == "hll":
                if obj["background"]:
                    hl = obj['background']
                    hl_comment = "# Highlight Line"
                continue

            attr = []
            if obj["bold"]:
                attr.append("bold")
            if obj["italic"]:
                attr.append("italic")
            if obj["underline"]:
                attr.append("underline")
            if obj["border"]:
                attr.append("border:%s" % obj["border"])
            if obj["background"]:
                attr.append("bg:%s" % obj["background"])
            if obj["foreground"]:
                attr.append("%s" % obj["foreground"])

            text.append([c, attr, ""])
            length = len(c)
            if length > max_length:
                max_length = length
        else:
            print("ERROR: %s: Unrecognized Class!" % obj["class"])
            undetected.append(obj)

    text.append(["Text", [fg], fg_comment])
    text.sort()

    with open(join(folder, "%s.py" % lname), "w") as w:
        w.write(
            HEADER + (
                CLASS_START % (
                    name, bg, bg_comment, hl, hl_comment,
                    format_rules(text, undetected, invalid, max_length)
                )
            )
        )
