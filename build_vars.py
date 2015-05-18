"""
Ensure all modules are found for Pyinstaller builds.

Due to dynamic importing of the modules, not all modules are found by Pyinstaller.
"""
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
# These are files or directories to
# process
#####################################
data_to_crawl = [
    "pymdown/data"
]


hidden_imports_to_crawl = [
    'pymdown_styles',
    'pymdown_lexers'
]


#####################################
# Crawl Functions
#####################################
def crawl_data(src, dest):
    """Crawl data."""
    for target in src:
        if os.path.isfile(target):
            dest.append((target, "./%s" % target, "DATA"))
        else:
            for f in os.listdir(target):
                file_path = os.path.join(target, f)
                if os.path.isfile(file_path) and not f.startswith((".", "~")) and not f.endswith('.py'):
                    name = '/'.join([target, f])
                    dest.append((name, "./%s" % name, "DATA"))


def crawl_hidden_imports(src, dest, paths):
    """Crawl hidden imports."""
    import pkgutil
    for mod in src:
        pkg = pkgutil.get_loader(mod)
        if getattr(pkg, 'archive', None) is None:
            folder = pkg.filename
            dest.append(pkg.fullname)
            for f in os.listdir(folder):
                if f != "__init__.py" and f.endswith('.py'):
                    dest.append('.'.join([pkg.fullname, f]))
        else:
            handle_egg(pkg.archive, paths, dest)


def handle_egg(archive, dest, egg_modules):
    """Handle an egg import."""

    def is_egg(archive):
        """
        Check if is an egg that we will accept.

        Egg must start with 'pymdown'.
        """

        egg_extension = "py%d.%d.egg" % (sys.version_info.major, sys.version_info.minor)
        egg_start = "pymdown"
        return (
            os.path.isfile(archive) and
            os.path.basename(archive).endswith(egg_extension) and
            os.path.basename(archive).startswith(egg_start)
        )

    def hidden_egg_modules(archive, dest):
        """Add egg modules to hidden imports."""

        with zipfile.ZipFile(archive, 'r') as z:
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

    if is_egg(archive):
        dest.append(archive)
        hidden_egg_modules(archive, egg_modules)

crawl_data(data_to_crawl, data)
crawl_hidden_imports(hidden_imports_to_crawl, hidden_imports, paths)


#####################################
# Print Results
#####################################
def print_vars(label, src):
    """Print specified variable."""

    print("--- %s ---" % label)
    for s in src:
        print(s)
    print('')


def print_all_vars():
    """Print all the variables."""

    print('====== Processed Spec Variables =====')
    print_vars('Data', data)
    print_vars('Hidden Imports', hidden_imports)
    print_vars("Paths", paths)


if __name__ == "__main__":
    print_all_vars()
