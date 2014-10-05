import os
import glob
from PyInstaller.hooks.hookutils import exec_statement


def get_submodules(module):
    """
    Get list of markdown extensions
    """
    statement = 'import %s; print %s.__path__[0]' % (module, module)
    mod_path = os.path.join(exec_statement(statement))
    files = glob.glob(mod_path + '/*.py')
    modules = []
    print(mod_path)

    for f in files:
        mod = os.path.splitext(os.path.basename(f))[0]
        # Skip __init__ module.
        if mod == '__init__':
            continue
        modules.append('%s.%s' % (module, mod))
        print('%s.%s' % (module, mod))

    return modules
