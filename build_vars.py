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
import subprocess
import sys

PY3 = sys.version_info >= (3, 0)

#####################################
# Vairables to be used in spec file
#####################################
data = []
eggs = []
hidden_imports = [
    # This should get automated in the future
    "pymdown_lexers.trex",
    "pymdown_styles.tomorrow",
    "pymdown_styles.tomorrownight",
    "pymdown_styles.tomorrownightblue",
    "pymdown_styles.tomorrownightbright",
    "pymdown_styles.tomorrownighteighties",
    "pymdown_styles.github",
    "pymdown_styles.github2"
]

#####################################
# This are files or directories to
# process
#####################################
data_to_crawl = [
    "LICENSE",
    "pymdown.json",
    "markdown/LICENSE.md",
    "pygments/LICENSE"
]

eggs_to_crawl = [
    "pymdown-lexers",
    "pymdown-styles"
]

hidden_imports_to_crawl = [
    "markdown/extensions",
    "pygments/styles",
    "pygments/lexers",
    "pygments/formatters",
    "pymdown"
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


def create_egg(directory):
    """
    Launch the build process
    """

    okay = True

    cwd = os.getcwd()
    os.chdir(directory)

    # Setup build process
    for command in ('build', 'bdist_egg'):
        if command == 'build':
            print("Building egg in %s..." % directory)
        elif command == 'bdist_egg':
            print("Creating egg in %s..." % directory)
        process = subprocess.Popen(
            [sys.executable, 'setup.py', command],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False
        )

        for line in iter(process.stdout.readline, b''):
            sys.stdout.write(line.decode('utf-8') if PY3 else line)
        process.communicate()

        # Check for bad error code
        if process.returncode:
            print("Compilation failed!")
            okay = False
            break

    os.chdir(cwd)

    return okay


def crawl_eggs(src, dest):
    for directory in src:
        setup = os.path.join(directory, "setup.py")
        if os.path.exists(setup):
            if create_egg(directory):
                dist = os.path.join(directory, 'dist')
                for f in os.listdir(dist):
                    if f.endswith('.egg'):
                        dest.append(os.path.abspath(os.path.join(dist, f)))
            else:
                print("Failed to generate egg for %s" % directory)

crawl_eggs(eggs_to_crawl, eggs)
crawl_data(data_to_crawl, data)
crawl_hidden_imports(hidden_imports_to_crawl, hidden_imports)


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
    print_vars('Eggs', eggs)
