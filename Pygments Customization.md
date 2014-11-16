[TOC]
# Overview
Pygments allows for people to write their own lexers and styles, but they need to have an entry point of `pymdown.lexers` or `pymdown.styles` for the respective plugin type.  This can only be done by either directly adding your plugin to the Pygments package, or creating and installing your own package that defines the entry points as mentioned.  If you know how to create your own package and install it, PyMdown should able to use it, but you have to play with the pyinstaller hooks if compiling a binary.  Another way is to create an egg that defines the proper entry point, and add the egg to the system path.

# Adding to Provided Custom Eggs or Create Your Own
PyMdown comes with a couple of optional eggs that can be included.  One is for [lexers](https://github.com/facelessuser/PyMdown/tree/master/pymdown-lexers), the other is for [styles](https://github.com/facelessuser/PyMdown/tree/master/pymdown-styles).  You can create your own lexer and/or style and drop it in with the others.  Then just edit the `__init__.py` file and expose your module (style example shown below):

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

Optionally, you can follow the pattern of the provided custom lexers and styles, and have your own egg built along side or in place of the the provided ones.  If you add your own custom egg, its name must start with `pymdown_` as the egg will not be loaded if its name does not start with `pymdown_` and end with the appropriate python version.

# Generate and Include Eggs
A script is provided for generating custom eggs.  It is called [gen_egg.py](https://github.com/facelessuser/PyMdown/blob/master/tools/gen_egg.py).  It can be run from PyMdown's root directory.  To build the provided custom eggs, do the following from the project's root directory:

```
python tools/gen_egg.py pymdown-styles
python tools/gen_egg.py pymdown-lexers
```

The eggs will be generated and copied to the an `eggs` folder.  Now when compiling PyMdown, the eggs will be bundled in the application and be usable, and if not compiling, the eggs will be included in the system path and be usable.  In both cases the eggs modules will be accessible as if they were native to Pygments.  As mentioned before, PyMdown will not load the egg if it doesn't start with `pymdown_`.  The generation script will append the Python version to the end of the egg name, so only when PyMdown is run with or built with the same version of Python that created the egg will it get loaded.
