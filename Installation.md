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
| [Python Markdown 2.5.2+][py_md] | Python Mardkown must be installed as it is the Markdown parser that is being used.  It must be 2.5.2 or greater as certain fixes are needed that were added in 2.5.2. |
| [Pygments 2.0rc1+ (optional)][pygments] | If Pygments Syntax highlighting is desired, Pygments must be installed.  This can be omitted, and code blocks (if using the CodeHilite extension) will be formatter for use with Javascript code highlighters. |
| [PyYaml 3.10+][pyyaml] | PyYaml is required. Older versions may work, but I am arbitrarily specifying 3.10 as the earliest I am aware of that works. |


# Build

If building, you will need to download the latest PyInstaller from [Github](https://github.com/pyinstaller/pyinstaller).  Just unzip and ensure the main folder is named `pyinstaller`.  Then from PyMdown's root directory, run `python build -c`.  The binary should be created in the `dist` folder.  This is regularly tested on Windows 7 and OSX 10.10.  Linux may require some playing around if it doesn't work out of the box.

In the future, I do plan on allowing this run from an installed Pyinstaller opposed to a version copied into the project, but currently I don't support it mainly because on Windows I build with a portable Python (WinPython), and I haven't spent any time yet to get it running proper without having it copied in the project.

# Installation
You can download PyMdown and run it as a script bundle, or build and copy the binary in your path.  PyMdown on the first run will unpack user files to `~\.PyMdown` on Windows, `~/.PyMdown` on OSX and `~/.config/PyMdown` on Linux.
