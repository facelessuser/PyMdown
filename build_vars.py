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

data = [
    ("LICENSE", "./LICENSE", "DATA"),
    ("pymdown.json", "./pymdown.json", "DATA"),
    ("markdown/LICENSE.md", "./markdown/LICENSE.md", "DATA"),
    ("pygments/LICENSE", "./pygments/LICENSE", "DATA")
]

data_to_crawl = [
]

for directory in data_to_crawl:
    for f in os.listdir(directory):
        if f.endswith(".css"):
            name = '/'.join([directory, f])
            data.append((name, "./%s" % name, "DATA"))

imports = [
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

imports_to_crawl = [
    "markdown/extensions",
    "pygments/styles",
    "pygments/lexers",
    "pygments/formatters",
    "pymdown"
]

for directory in imports_to_crawl:
    imports.append(directory.replace('/', '.'))
    for f in os.listdir(directory):
        if f != "__init__.py" and f.endswith('.py'):
            imports.append('/'.join([directory, f])[:-3].replace('/', '.'))

eggs = []

egg_folders_to_crawl = [
    "pymdown-lexers",
    "pymdown-styles"
]

for directory in egg_folders_to_crawl:
    setup = os.path.join(directory, "setup.py")
    if os.path.exists(setup):
        if create_egg(directory):
            dist = os.path.join(directory, 'dist')
            for f in os.listdir(dist):
                if f.endswith('.egg'):
                    eggs.append(os.path.abspath(os.path.join(dist, f)))
        else:
            print("Failed to generate egg for %s" % directory)

# print(data)
# print(imports)
# print(eggs)
