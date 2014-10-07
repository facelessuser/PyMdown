#!/usr/bin/python
from __future__ import print_function
import sys
from os.path import dirname, abspath, join
from os import path, mkdir, chdir
import shutil
import argparse
import subprocess

PY3 = sys.version_info >= (3, 0)
if PY3:
    unicode_str = str
else:
    unicode_str = unicode  # flake8: noqa

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

SPEC = '''# -*- mode: python -*-

block_cipher = None


a = Analysis(%(main)s,
             pathex=%(directory)s,
             hiddenimports=%(hidden)s,
             hookspath=%(hook)s,
             runtime_hooks=None)
a.datas = %(data)s
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=%(exe)s,
          debug=False,
          strip=None,
          icon=%(icon)s,
          console=True )
'''


def build_spec_file(obj):
    proj_path = path.dirname(obj.script)
    sys.path.append(proj_path)
    try:
        import build_vars
    except:
        class build_vars(object):
            hidden_imports = []
            data = []
            hookpaths = []
            paths = []

            @staticmethod
            def print_vars(label, src):
                pass

            @staticmethod
            def print_all_vars():
                pass

    build_vars.print_all_vars()

    with open("%s.spec" % obj.name, "w") as f:
        f.write(
            SPEC % {
                "main": repr([obj.script]),
                "directory": repr([path.dirname(obj.script)] + build_vars.paths),
                "hidden": repr(build_vars.hidden_imports),
                "hook": repr(build_vars.hookpaths),
                "data": repr(build_vars.data),
                "exe": repr(path.basename(obj.app)),
                "icon": repr(obj.icon)
            }
        )


class Args(object):
    def __init__(
        self, script, name, gui, clean, ext,
        icon=None, portable=False
    ):
        """
        Build arguments
        """

        self.gui = bool(gui)
        self.name = name
        self.clean = bool(clean)
        self.icon = abspath(icon) if icon is not None else icon
        self.script = script
        self.extension = ext
        self.portable = portable


class BuildParams(object):
    """
    Build parametes
    """

    python_bin_path = None
    python_executable = None
    pyinstaller_script = None
    out_dir = None
    script = None
    dist_path = None
    name = None
    clean = None
    extension = None
    icon = None
    portable = None
    spec_path = None


def parse_settings(args, obj):
    """
    Configure build parameters based on arguments
    """

    err = False

    script_path = dirname(abspath(sys.argv[0]))
    obj.python_bin_path = dirname(sys.executable)
    obj.python_bin = sys.executable
    obj.pyinstaller_script = join(script_path, "pyinstaller", "pyinstaller.py")
    obj.out_dir = join(script_path, "build")
    obj.dist_path = join(script_path, "dist")
    obj.name = args.name
    obj.extension = args.extension
    obj.script = path.abspath(path.normpath(args.script))
    obj.icon = args.icon
    obj.clean = args.clean
    obj.portable = args.portable
    obj.spec = path.join(path.dirname(obj.script), '%s.spec' % obj.name)

    if not path.exists(obj.script):
        print("Could not find %s!" % obj.script)
        err = True
    elif args.icon is not None and not path.exists(args.icon):
        print("Could not find %s!" % obj.icon)
        err = True
    elif obj.pyinstaller_script is None or not path.exists(obj.pyinstaller_script):
        print("Could not find pyinstaller.py!")
        err |= True

    if not path.exists(obj.out_dir):
        err |= create_dir(obj.out_dir)
    elif not path.isdir(obj.out_dir):
        print("%s is not a directory!" % obj.out_dir)
        err |= True

    # Get executable name to build
    if not err:
        obj.app = path.join(obj.dist_path, obj.name) + obj.extension
    return err


def create_dir(directory):
    """
    Create build directory
    """

    err = False
    try:
        print("Creating %s..." % directory)
        mkdir(directory)
    except:
        print("Could not create %s!" % directory)
        err = True
    return err


def clean_build(build_dir):
    """
    Clean the build directory
    """

    err = False
    try:
        print("Cleaning %s..." % build_dir)
        shutil.rmtree(build_dir)
    except:
        print("Failed to clean %s!" % build_dir)
        err = True
    return err


def parse_options(args, obj):
    """
    Parse the build parameters and build the pyinstaller build command
    """

    err = False

    # Parse Settings file
    if not err:
        err = parse_settings(args, obj)

    # See if cleaning is required
    if not err and args.clean and path.exists(obj.out_dir):
        err = clean_build(obj.out_dir)

    if not err:
        build_spec_file(obj)

    # Construct build params for build processs
    if not err:
        obj.params = (
            [("python" if obj.portable else obj.python_bin), obj.pyinstaller_script, '-F'] +
            (['--clean'] if args.clean is not None else []) +
            (['-w', '--workpath=%s' % obj.out_dir] if args.gui else ['--workpath=%s' % obj.out_dir]) +
            ['--distpath=%s' % obj.dist_path] +
            ['-y', obj.spec]
            # ['--log-level=DEBUG']
        )
    return err


def build(obj):
    """
    Launch the build process
    """

    err = False

    if obj.portable:
        chdir(obj.python_bin_path)

    # Setup build process
    process = subprocess.Popen(
        obj.params,
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
        err = True

    return err


def main():
    """
    Setup the build process and initiate it
    """

    parser = argparse.ArgumentParser(prog='Build', description='Python script for building apps for Pyinstaller')
    # Flag arguments
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parser.add_argument('--clean', '-c', action='store_true', default=False, help='Clean build before re-building.')
    parser.add_argument('--gui', '-g', action='store_true', default=False, help='GUI app')
    parser.add_argument('--portable', '-p', action='store_true', default=False, help='Build with portable python (windows)')
    # parser.add_argument('--imports', default=None, nargs="*", help='Include hidden imports')
    parser.add_argument('--icon', '-i', default=None, nargs="?", help='App icon')
    # parser.add_argument('script', default=None, help='Main script')
    # parser.add_argument('name', default=None, help='Name of app')
    inputs = parser.parse_args()
    if _PLATFORM == "windows":
        args = Args(
            "__main__.py", "pymdown", inputs.gui, inputs.clean, ".exe", inputs.icon, inputs.portable
        )
    elif _PLATFORM == "osx":
        args = Args(
            "__main__.py", "pymdown", inputs.gui, inputs.clean, ".app" if inputs.gui else '', inputs.icon
        )
    else:
        args = Args(
            "__main__.py", "pymdown", inputs.gui, inputs.clean, '', inputs.icon
        )

    # Parse options
    build_params = BuildParams()
    err = parse_options(args, build_params)

    # Build executable
    if not err:
        err = build(build_params)

    return err

if __name__ == "__main__":
    sys.exit(main())
