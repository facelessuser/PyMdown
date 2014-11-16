---
references:
- _references/references.md
---
[TOC]
# Overview
PyMdown can be downloaded and run directly.  If desired, you can write a batch file front end on windows, or something else on other system.  I personally use [Pyinstaller][pyinstaller] to build a binary that I drop in my systems path so I can run it from anywhere; the procedure for this is outlined [below](#below).

# Requirements
In order for PyMdown to work, there are a couple of prerequisites.


| Name | Details |
|------|---------|
| [Python Markdown 2.5 (experimental)][py_md] | There are a number of fixes that occurred after version 2.5.1 that, at the time of writing this, have not been released.  So currently, you can either download the main branch on Github and drop the `markdown` folder in the root of this project, or you can download the main branch and install via `python setup.py build` and `python setup.py install`.  As soon as the next version is released, you will simply be able to use `pip install markdown`. The current revision that I am using is https://github.com/waylan/Python-Markdown/archive/57633f1743cc16e16c140cc92f860c62d872b6cc.zip |
| [Pygments 2.0rc1+ (optional)][pygments] | If Pygments Syntax highlighting is desired, Pygments must be installed.  This can be omitted, and code blocks (if using the CodeHilite extension) will be formatter for use with Javascript code highlighters. |
| [PyYaml][pyyaml] | PyYaml is required. |


# Build

If building, you will need to download the latest PyInstaller from [Github](https://github.com/pyinstaller/pyinstaller).  Just unzip and ensure the main folder is named `pyinstaller`.  Then from PyMdown's root directory, run `python build -c`.  The binary should be created in the `dist` folder.  This is regularly tested on Windows 7 and OSX 10.10.  Linux may require some playing around if it doesn't work out of the box.

In the future, I do plan on allowing this run from an installed Pyinstaller opposed to a version copied into the project, but currently I don't support it mainly because on Windows I build with a portable Python (WinPython), and I haven't spent any time yet to get it running proper without having it copied in the project.

# Installation
You can download PyMdown and run it as a script bundle, or build and copy the binary in your path.  PyMdown on the first run will unpack user files to `~\.PyMdown` on Windows, `~/.PyMdown` on OSX and `~/.config/PyMdown` on Linux.
