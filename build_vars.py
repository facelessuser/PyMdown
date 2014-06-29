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
to_crawl = [
    "markdown/extensions",
    "pygments/styles",
    "pygments/lexers",
    "pygments/formatters",
    "mdownx"
]

data = [
    ("stylesheets/default.css", "./stylesheets/default.css", "DATA"),
    ("mdown.json", "./mdown.json", "DATA")
]

imports = []
for directory in to_crawl:
    imports.append(directory.replace('/', '.'))
    for f in os.listdir(directory):
        if f != "__init__.py" and f.endswith('.py'):
            imports.append(os.path.join(directory, f)[:-3].replace('/', '.'))

# print(imports)
