import os
from PyInstaller.utils.misc import get_code_object


def retarget(mod, new_file):
    mod.__init__(
        mod.__name__,
        new_file,
        get_code_object(new_file)
    )


def hook(mod):
    # Replace mod with fake 'codehilite' module that works with pyinstaller.
    hook_dir = os.path.abspath(os.path.dirname(__file__))
    fake_file = os.path.join(hook_dir, 'fake', 'fake-codehilite.py')
    retarget(mod, fake_file)
    return mod
