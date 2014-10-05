import os
import PyInstaller


def hook(mod):
    # Replace mod by fake 'codehilite' module.
    hook_dir = os.path.abspath(os.path.dirname(__file__))
    fake_file = os.path.join(hook_dir, 'fake', 'fake-codehilite.py')
    new_code_object = PyInstaller.utils.misc.get_code_object(fake_file)
    mod = PyInstaller.depend.modules.PyModule(
        'markdown.extensions.codehilite', fake_file, new_code_object
    )
    return mod
