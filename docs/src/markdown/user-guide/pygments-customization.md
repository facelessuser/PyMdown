# Pygments Customization

## Overview

Pygments allows for people to write their own lexers and styles, but they need to have an entry point of `pygments.lexers` or `pygments.styles` for the respective plugin type.  This can only be done by either directly adding your plugin to the Pygments package, or creating and installing your own package that defines the entry points as mentioned.  If you know how to create your own package and install it, PyMdown should be able to use it.

## Create Your Own Pygments Styles and Lexers

PyMdown comes with a couple of optional [styles][pymdown-styles] and [lexers][pymdown-lexers] that can be included.  They don't offer anything that is **needed**, but you can use these two repositories as an example.

Once the lexer or style is written, you have to edit the `__init__.py` file and expose your module (style example shown below):

```py3
from .tomorrow import TomorrowStyle
from .tomorrownight import TomorrownightStyle
from .tomorrownightblue import TomorrownightblueStyle
from .tomorrownightbright import TomorrownightbrightStyle
from .tomorrownighteighties import TomorrownighteightiesStyle
from .github import GithubStyle
from .github2 import Github2Style
```

Then edit the `setup.py` file and define the entry point (style example shown below):

```py3
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

--8<-- "refs.md"
