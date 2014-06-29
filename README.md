# Mdown
Mdown is CLI tool to convert or even batch convert markdown files to HTML. It can also accept a file stream.  It was inspired by https://github.com/revolunet/sublimetext-markdown-preview.

# Status
This is in an Alpha state, though it is very useable.  Because of the Alpha state, things are in flux and are subject to change without warning.

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
    - **absolutepath**: Converts local file paths from relative to absolute for things like links, images, etc.  This is automatically done on all previews.  It can be configured to run all the time outside of previews in the settings file, and it can take a hardcoded path `absolutepath(base_path=/my/path)` or a dynamic path `absolutepath(base_path=${BASE_PATH})` that can take the base\_path fed in on the command line or calculated from the source files path.  If you set this in the settings file, keep in mind the settings file overrides preview's settings.
    - **b64**: Base64 encode local image files. If can be enabled and configured in the settings file and can take a hardcoded path `b64(base_path=/my/path)` or it can take a dynamic base\_path `b64(base_path=${BASE_PATH})` fed in on the command line or calculated from the source files path.
    - **insert**: Add <ins>test</ins> tags by using ++test++. Can be enabled in the settings file.
    - **delete**: Add <del>test</del> tags by using ~~test~~. Can be enabled in the settings file.
    - **magiclink**: Search for and convert http or ftp links to actual HTML links for lazy link creation. Can be enabled in the settings file.
    - **critic**: Cannot be set in the settings file. It is configured automatically, and can only its behaviour can only be modifid via the command line.  In its current form, it can output in HTML a highlighted critic form to make it more readable using the -c option (maybe in the future it might be able to do more).  The automatic behaviour is to strip out critic marks when outputting HTML.  It either accepts all changes or rejects all changes (by default it accepts, but with the -r option it can reject instead).

        insert, delete, and substitution

        ![Insert, Delete, and Substitution](https://dl.dropboxusercontent.com/u/342698/mdown/insert_delete_sub.png)

        highlight and comments

        ![Highlight and Comments](https://dl.dropboxusercontent.com/u/342698/mdown/highlight_comment.png)

    - **mdownx**: currently loads insert, delete, b64, and magiclink

# Styles and Configuration

## Syntax Highlighting with Pygments
Syntax highlighting can be done in fenced blocks when enabling the `codehilite` extension.  Its styles etc. can be configured in the settings file as well. Here is an example:

```javascript
    "extensions": [
        "extra",
        "toc",
        "codehilite(guess_lang=False,pygments_style=tomorrownighteighties)"
    ]
```

Notice the syntax style is set with the `pygments_style` key.

## How To Use highlight.js Syntax Highlighting
You will have to provide the highlight.js script and preferred CSS theme and add them to the output via these settings:

```javascript
    // Select your CSS for you output html
    // or you can have it all contained in your HTML template
    // Add your highlight.js theme here as well.
    //
    // Can be an array of stylesheets or "default"
    // "default" can also be an entry in the array.
    // If it points to a physical file, it will be included.
    "css_style_sheet": ["default"],

    // Load up highlight.js or other js scripts
    //
    // Can be an array of scripts.
    // If it points to a physical file, it will be included.
    "js_scripts": [],
```

Then a special parameter was added into the `codehilite` extension to manually enable highlight.js support.

```javascript
    "codehilite(highlight_js=True)"
```

# Add More CSS and JS Files
Add them to the provided settings:

```javascript
    // Select your CSS for you output html
    // or you can have it all contained in your HTML template
    // Add your highlight.js theme here as well.
    //
    // Can be an array of stylesheets or "default"
    // "default" can also be an entry in the array.
    // If it points to a physical file, it will be included.
    "css_style_sheet": ["default"],

    // Load up highlight.js or other js scripts
    //
    // Can be an array of scripts.
    // If it points to a physical file, it will be included.
    "js_scripts": [],
```

## Change the HTML Template
This can be done here:

```javascript
    // Your HTML template
    "html_template": "default",
```

# Command Line

```
usage: mdown [-h] [--version] [--quiet] [--preview] [--critic | --critic-dump]
             [--reject] [--terminal] [--output OUTPUT] [--stream]
             [--title TITLE] [--encoding ENCODING] [--basepath BASEPATH]
             [markdown [markdown ...]]

Markdown generator

positional arguments:
  markdown              Markdown file(s) or file pattern(s).

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --quiet, -q           No messages on stdout.
  --preview, -p         Output to preview (temp file). --output will be
                        ignored.
  --critic, -c          Show critic marks in a viewable html output.
  --critic-dump, -C     Process critic marks, dumps file(s), and exits.
  --reject, -r          Reject propossed critic marks when using in normal
                        processing and --critic-dump processing
  --terminal, -t        Print to terminal (stdout).
  --output OUTPUT, -o OUTPUT
                        Output directory can be a directory or file_name. Use
                        ${count} when exporting multiple files and using a
                        file pattern.
  --stream, -s          Streaming input. markdown file inputs will be ignored.
  --title TITLE, -T TITLE
                        Title for HTML.
  --encoding ENCODING, -e ENCODING
                        Encoding for input.
  --basepath BASEPATH, -b BASEPATH
                        The basepath location mdown should use.
```

# Credits
- Uses a slightly modified https://pypi.python.org/pypi/Markdown
- Uses the development branch of Pygments for Python 3 supporthttp://pygments.org/
- Borrowed and modified default CSS file from https://github.com/revolunet/sublimetext-markdown-preview.  Also, the original inspiration for this project.
- Includes Tomorrow Themes for Pygment from https://github.com/MozMorris/tomorrow-pygments

# Build
- Download or clone Pyinstaller main branch (latest release won't work; the dev branch is needed) from github into the mdown project folder https://github.com/pyinstaller/pyinstaller
- Using Python 2 run `python build.py -c`
- Binary will be in the `mdown/dist` folder

# TODO
- ~~Critic markup~~
    - ~~Allow for easy optional visual of critic markup in HTML~~
    - ~~When normal parsing of a file with critic markup:~~
        - ~~Remove comments~~
        - ~~ignore marks~~
        - ~~don't show removed~~
        - ~~show inserts as normal~~
        - ~~substitute is converted to show just the inserts~~
    - ~~Allow a reject option parse a file with critic markup in the reverse:~~
        - ~~Remove comments~~
        - ~~ignore marks~~
        - ~~don't show added~~
        - ~~show removed as normal~~
        - ~~substitute is converted to show just the removed~~
    - ~~Front in preprocessor in CLI to dump the markdown without crtic marks if desired~~
- Maybe more extensions
- Maybe a better batch output file pattern system
- Maybe inject javascript into current test documents to verify certain expected things are in output HTML
- ...stuff I havn't yet thought of...

# License
MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#3rd Party Licenses

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
