from .hook_helper import get_submodules

hiddenimports = get_submodules('pygments.formatters')
hiddenimports += get_submodules('pygments.lexers')
hiddenimports += get_submodules('pygments.styles')
