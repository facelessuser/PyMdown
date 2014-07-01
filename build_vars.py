#####################################
# For pyinstaller build to ensure
# all modules are found.  Due to
# sneaky importing because of the
# dynamic nature of the modules,
# not all modules are found by
# pyinstaller.
#
# Not all of this crap is needed,
# but I don't feel like figuring out
# which ones shouldn't be included.
#####################################
import os

data = [
    ("stylesheets/default.css", "./stylesheets/default.css", "DATA"),
    ("mdown.json", "./mdown.json", "DATA"),
    ("highlight.js/highlight.pack.js", "./highlight.js/highlight.pack.js", "DATA"),
    ("highlight.js/LICENSE", "./highlight.js/LICENSE", "DATA"),
    ("markdown/LICENSE.md", "./markdown/LICENSE.md", "DATA"),
    ("pygments/LICENSE", "./pygments/LICENSE", "DATA")
]

data_to_crawl = [
    "highlight.js/styles"
]

for directory in data_to_crawl:
    for f in os.listdir(directory):
        if f.endswith(".css"):
            name = '/'.join([directory, f])
            data.append((name, "./%s" % name, "DATA"))


imports = []

imports_to_crawl = [
    "markdown/extensions",
    "pygments/styles",
    "pygments/lexers",
    "pygments/formatters",
    "mdownx"
]

for directory in imports_to_crawl:
    imports.append(directory.replace('/', '.'))
    for f in os.listdir(directory):
        if f != "__init__.py" and f.endswith('.py'):
            imports.append('/'.join([directory, f])[:-3].replace('/', '.'))

# print(data)
# print(imports)
