#####################################
# To ensure all modules are found
# for Pyinstaller builds. Due to
# dynamic importing of the modules,
# not all modules are found by
# Pyinstaller.
#####################################
import os
import sys
import zipfile

PY3 = sys.version_info >= (3, 0)

#####################################
# Vairables to be used in spec file
#####################################
data = []
hidden_imports = []
paths = []
hookpaths = ['pyinstaller_hooks']

#####################################
# This are files or directories to
# process
#####################################
data_to_crawl = [
    "data/licenses.txt",
    "pymdown.cfg"
]

hidden_imports_to_crawl = []

eggs_to_crawl = [
    'eggs'
]


#####################################
# Crawl Functions
#####################################
def crawl_data(src, dest):
    for target in src:
        if os.path.isfile(target):
            dest.append((target, "./%s" % target, "DATA"))
        else:
            for f in os.listdir(target):
                if f.endswith(".css"):
                    name = '/'.join([target, f])
                    dest.append((name, "./%s" % name, "DATA"))


def crawl_hidden_imports(src, dest):
    for directory in src:
        dest.append(directory.replace('/', '.'))
        for f in os.listdir(directory):
            if f != "__init__.py" and f.endswith('.py'):
                dest.append('/'.join([directory, f])[:-3].replace('/', '.'))


def crawl_eggs(src, dest, egg_modules):
    def is_egg(egg_file):
        egg_extension = "py%d.%d.egg" % (sys.version_info.major, sys.version_info.minor)
        egg_start = "pymdown"
        return (
            os.path.isfile(egg_file) and
            os.path.basename(egg_file).endswith(egg_extension) and
            os.path.basename(egg_file).startswith(egg_start)
        )

    def hidden_egg_modules(src, dest):
        with zipfile.ZipFile(target, 'r') as z:
            text = z.read(z.getinfo('EGG-INFO/SOURCES.txt'))
            if PY3:
                text = text.decode('utf-8')
            for line in text.split('\n'):
                line = line.replace('\r', '')
                if (
                    line.endswith('.py') and
                    not line.endswith('/__init__.py') and
                    line != 'setup.py'
                ):
                    dest.append(line.replace('/', '.')[:-3])

    for location in src:
        if os.path.exists(location) and os.path.isdir(location):
            for f in os.listdir(location):
                target = os.path.abspath(os.path.join(location, f))
                if is_egg(target):
                    dest.append(target)
                    hidden_egg_modules(target, egg_modules)

        elif os.path.isfile(location):
            target = os.path.abspath(location)
            if is_egg(target):
                dest.append(target)

crawl_data(data_to_crawl, data)
crawl_hidden_imports(hidden_imports_to_crawl, hidden_imports)
crawl_eggs(eggs_to_crawl, paths, hidden_imports)


#####################################
# Print Results
#####################################
def print_vars(label, src):
    print("--- %s ---" % label)
    for s in src:
        print(s)
    print('')


def print_all_vars():
    print('====== Processed Spec Variables =====')
    print_vars('Data', data)
    print_vars('Hidden Imports', hidden_imports)
    print_vars("Paths", paths)


if __name__ == "__main__":
    print_all_vars()
