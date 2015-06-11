# Installation {: .doctitle}
Installation of PyMdown.

---

## Overview
Pymdown is built on top of a few requirements.  If installing, the requirements will be installed automatically.

## Requirements
In order for PyMdown to work, there are a couple of prerequisites.

| Name | Required |Details |
|------|----------|--------|
| [Python Markdown 2.6.0+][py_md] | Yes |Python Markdown must be installed as it is the Markdown parser that is being used. |
| [PyMdown Extensions](https://github.com/facelessuser/pymdown-extensions) | Yes | Extensions for PyMdown. |
| [PyYaml 3.10+][pyyaml] | Yes | Older versions may work, but I am arbitrarily specifying 3.10 as the earliest I am aware of that works. |
| [Pygments 2.0.1+ (optional)][pygments] | No | If Pygments Syntax highlighting is desired, Pygments must be installed.  This can be omitted, and code blocks (if using the CodeHilite extension) will be formatter for use with JavaScript code highlighters. |
| [PyMdown Styles](https://github.com/facelessuser/pymdown-styles) | No | Optional package that adds a couple of custom Pygments styles. This is not required, but is a great example if you want to create your own style package. |
| [PyMdown Lexers](https://github.com/facelessuser/pymdown-lexers) | No | Optional package that adds a couple of non-standard lexers, but nothing of substantial interest. This is a great example for adding your own custom lexers. |

## Installation
You can download PyMdown and run it as a script bundle.  To install, run `#!bash python setup.py build` and `#!bash python setup.py install`.  You should be able to access PyMdown from the command line via `pymdown` or `pymdownX.X` where `X.X` is your python version.  PyMdown on the first run will unpack user files to `~\.PyMdown` on Windows, `~/.PyMdown` on OSX and `~/.config/PyMdown` on Linux.

If you would like to modify the code, you install it via: `#!bash pip install --editable .`.  This method will allow you to instantly see your changes without reinstalling.  If you want to do this in a virtual machine, you can.

[py_md]: https://pythonhosted.org/Markdown/
[pygments]: http://pygments.org/
[pyyaml]: http://pyyaml.org/
