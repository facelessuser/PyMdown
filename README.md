# Mdown
Mdown is CLI tool to convert or even batch convert markdown files to HTML. It can also accept a file stream.

# Features
- Python 2 and 3 compatible (but executables built with Python 2 using Pyinstaller)
- Should run on OSX, Windows, and Linux
- Receive multiple files or file patterns to process
- Receive input file stream for conversion
- Configurable options file to tweak Python's Markdown package behavior
- Uses Pygments for syntax highighlighting or optionally highlight.js (you must provide highlight.js and highlight.js theme)
- Repo includes in `extras` a simple Sublime Text plugin to stream your files to mdown
- Preview option to open output in a browser intead
- Optionally all the default Markdown extensions, plus these optional mdownx extensions:
    - **absolutepath**: convert local file paths from relative to absolute
    - **b64**: base64 encode local image files
    - **insert**: add <ins>test</ins> tags by using ++test++
    - **delete**: add <del>test</del> tags by using ~~test~~
    - **magiclink**: search for and convert http or ftp links to actual HTML links for lazy link creation
    - **critic**: experimental extension to display a file marked up with critic tags in a more simple way. (must be the last extension added and essentially overrides all others)
    - **mdownx**: currently loads insert, delete, b64, and magiclink

# Credits
- Uses a slightly modified https://pypi.python.org/pypi/Markdown
- Uses the development branch of Pygments for Python 3 supporthttp://pygments.org/
- Borrowed and modified default CSS file from https://github.com/revolunet/sublimetext-markdown-preview
- Includes Tomorrow Themes for Pygment from https://github.com/MozMorris/tomorrow-pygments

# Build
- Download or clone Pyinstaller main branch (latest release won't work; the dev branch is needed) from github into the mdown project folder https://github.com/pyinstaller/pyinstaller
- Using Python 2 run `python build.py -c`
- Binary will be in the `mdown/dist` folder

# TODO
- Allow for easy visual of critic markup in HTML (maybe dynamically accept reject critic markup and and allow for access or saving of the modified markdown)
- Allow for accepting or rejecting critic markups and possibly output new markdown file
- Maybe more extensions
- Maybe a better batch output file pattern system
- Maybe inject javascript into current test documents to verify certain expected things are in output HTML
- ...stuff I havn't yet thought of...

# Licene
MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#3rd Party Licences

## Markdown
Copyright 2007, 2008 The Python Markdown Project (v. 1.7 and later)
Copyright 2004, 2005, 2006 Yuri Takhteyev (v. 0.2-1.6b)
Copyright 2004 Manfred Stienstra (the original version)

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

*   Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
*   Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
*   Neither the name of the <organization> nor the
    names of its contributors may be used to endorse or promote products
    derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE PYTHON MARKDOWN PROJECT ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL ANY CONTRIBUTORS TO THE PYTHON MARKDOWN PROJECT
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

# Pygments
Copyright (c) 2006-2013 by the respective authors (see AUTHORS file).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Markdown Preview
The MIT License (MIT)
Copyright © 2014 Julien Bouquillon, revolunet <julien@revolunet.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
