# Pygments Customization {: .doctitle}
Adding Pygments themes.

---

## Overview
Pygments allows for people to write their own lexers and styles, but they need to have an entry point of `pygments.lexers` or `pygments.styles` for the respective plugin type.  This can only be done by either directly adding your plugin to the Pygments package, or creating and installing your own package that defines the entry points as mentioned.  If you know how to create your own package and install it, PyMdown should be able to use it.  If you are compiling a binary with pyinstaller, you will have to [modify](#modify-pyinstaller-build) the `build_vars.py` file.

## Create Your Own Pygments Styles and Lexers
PyMdown comes with a couple of optional [styles](https://github.com/facelessuser/PyMdown/tree/master/pymdown-styles) and [lexers](https://github.com/facelessuser/PyMdown/tree/master/pymdown-lexers) that can be included.  They don't offer anything that is **needed**, but you can use these two repositories as an example.

Once the lexer or style is written, you have to edit the `__init__.py` file and expose your module (style example shown below):

```python
from .tomorrow import TomorrowStyle
from .tomorrownight import TomorrownightStyle
from .tomorrownightblue import TomorrownightblueStyle
from .tomorrownightbright import TomorrownightbrightStyle
from .tomorrownighteighties import TomorrownighteightiesStyle
from .github import GithubStyle
from .github2 import Github2Style
```

Then edit the `setup.py` file and define the entry point (style example shown below):

```python
from setuptools import setup, find_packages

entry_points = '''
[pygments.styles]
github=pymdown_styles:GithubStyle
github2=pymdown_styles:Github2Style
tomorrow=pymdown_styles:TomorrowStyle
tomorrownight=pymdown_styles:TomorrownightStyle
tomorrownightblue=pymdown_styles:TomorrownightblueStyle
tomorrownightbright=pymdown_styles:TomorrownightbrightStyle
tomorrownighteighties=pymdown_styles:TomorrownighteightiesStyle
'''

setup(
    name='pymdown-styles',
    version='1.0',
    packages=find_packages(),
    entry_points=entry_points,
    zip_safe=True
)
```

## Modify Pyinstaller Build
If you are building with a binary with Pyinstaller, and you want your custom package to be included, you can add the package name in `build_vars.py` under the `hidden_imports_to_crawl` list.

!!! Note "Note"
    In your custom packages, it is recommended to not specify dependencies in your python `setup.py` file as doing so may cause the PyMdown binary to fail when checking the package dependencies.

```python
hidden_imports_to_crawl = [
    'pymdown_styles',
    'pymdown_lexers'
]
```
