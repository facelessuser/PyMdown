# PyMdown
PyMdown is CLI tool to convert or even batch convert markdown files to HTML.  It can also generate HTML previews of markdown and auto-open them in a webbrowser. It can also accept a file stream.

# Status
This is in a **Beta** state.  Because of the **Beta** state, things are in flux and are subject to change without warning.

# Documentation
Though the documentation is currently still in flux and still being completed, it is found here: [PyMdown Documentation](http://facelessuser.github.io/PyMdown/)

# Requirements
The following must be installed in your Python

- [Python-Markdown 2.5.1+](https://pypi.python.org/pypi/Markdown)
    - Until the next version drops: https://github.com/waylan/Python-Markdown/archive/57633f1743cc16e16c140cc92f860c62d872b6cc.zip must specifically be used if the compiled version is desired.  A workaround hook was removed as this revision fixes the issue.  As soon as 2.5.2 or greater releases, the official channel can be used.
- [PyYaml](http://pyyaml.org)
- Optionally [Pygments 2.0 Dev branch](https://bitbucket.org/birkenfeld/pygments-main/overview) if you want Pygments syntax highlighting.  You can use something like HighlightJs otherwise.

# Features
- Should work on Python 2.7 and 3.0+ compatible (but executables are currently built with Python 2.7 using Pyinstaller). Usually tested on Python 2.7 and Python 3.4.  Can only be compiled with Pyinstaller for Python 2.7.
- Should run on OSX, Windows, and Linux.  Usually tested on Windows and OSX though.
- Receive multiple files or file patterns to process.
- Receive input file stream for conversion.
- Configurable options file to tweak Python's Markdown package behavior.
- Uses Pygments for syntax highighlighting.
- Preview option to preview output in a browser.
- Parses yaml or json frontmatter.
- Optionally all the default Markdown extensions, plus a number of custom pymdown extensions:

# Sublime Plugin
A sublime plugin that utilizes this app is found here: [sublime-pymdown](https://github.com/facelessuser/sublime-pymdown)

# Credits
- Built on top of https://pypi.python.org/pypi/Markdown
- Uses the development branch of Pygments for Python 3 support http://pygments.org/.
- Includes optional Tomorrow Themes for Pygment from https://github.com/MozMorris/tomorrow-pygments
- Currently includes the original github theme and the newest 2014 variant.
- Inspiration for the project came from https://github.com/revolunet/sublimetext-markdown-preview.

# License
MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#3rd Party Licenses
See [licenses](https://github.com/facelessuser/PyMdown/blob/master/data/licenses.txt).
