from .hook_helper import get_submodules

hiddenimports = get_submodules('markdown.extensions')
hiddenimports += get_submodules('pymdown')
