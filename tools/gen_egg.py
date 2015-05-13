"""
Create eggs for the given folders.
"""
import os
import subprocess
import sys
import shutil
PY3 = sys.version_info >= (3, 0)


def create_egg(directory):
    """ Launch the build process to create an egg. """

    okay = True

    cwd = os.getcwd()
    os.chdir(os.path.abspath(directory))

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


def crawl_eggs(src):
    """ Crawl the paths and create the egg for each source. """
    for directory in src:
        setup = os.path.join(directory, "setup.py")
        if os.path.exists(setup):
            if create_egg(directory):
                if not os.path.exists(egg_dir):
                    os.mkdir(egg_dir)
                if os.path.exists(egg_dir):
                    location = os.path.join(directory, 'dist')
                    egg_extension = "py%d.%d.egg" % (
                        sys.version_info.major,
                        sys.version_info.minor
                    )
                    egg_start = "pymdown"
                    for f in os.listdir(location):
                        target = os.path.abspath(os.path.join(location, f))
                        if (
                            os.path.isfile(target) and
                            f.endswith(egg_extension) and
                            f.startswith(egg_start)
                        ):
                            if target not in sys.path:
                                shutil.copyfile(
                                    target,
                                    os.path.join(egg_dir, os.path.basename(target))
                                )
                                print("Egg created!")
            else:
                print("Failed to generate egg for %s" % directory)

egg_dir = os.path.join(
    os.path.basename(
        os.path.abspath(
            os.path.dirname(sys.argv[0])
        )
    ),
    '..',
    'eggs'
)

crawl_eggs([sys.argv[1]])
