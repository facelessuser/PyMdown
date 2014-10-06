import os
import sys
# For some reason when this file is called for
# the hook method, relative imports no longer works
# so let's patch that.
HOOK_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(HOOK_DIR)
from hook_helper import retarget


def hook(mod):
    # Replace mod with fake 'codehilite' module that works with pyinstaller.
    fake_file = os.path.join(HOOK_DIR, 'fake', 'fake-codehilite.py')
    retarget(mod, fake_file)
    return mod
