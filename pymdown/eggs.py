"""
Load egg resources.

Places markdown in HTML with the specified CSS and JS etc.

This will probably be removed.

Licensed under MIT
Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>
"""
import sys
import os


def load_egg_resources():
    """
    Load egg resource.

    Add egg to system path if the name indicates it
    is for the current python version and for pymdown.
    This only runs if we are not in a pyinstaller environment.
    """

    if (
        not bool(getattr(sys, "frozen", 0)) and
        os.path.exists('eggs') and not os.path.isfile('eggs')
    ):  # pragma: no cover
        egg_extension = "py%d.%d.egg" % (
            sys.version_info.major, sys.version_info.minor
        )
        egg_start = "pymdown"
        for f in os.listdir("eggs"):
            target = os.path.abspath(os.path.join('eggs', f))
            if (
                os.path.isfile(target) and f.endswith(egg_extension) and
                f.startswith(egg_start)
            ):
                sys.path.append(target)

load_egg_resources()
