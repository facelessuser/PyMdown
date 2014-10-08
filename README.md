# PyMdown
PyMdown is CLI tool to convert or even batch convert markdown files to HTML.  It can also generate HTML previews of markdown and auto-open them in a webbrowser. It can also accept a file stream.

# Status
This is in a **Beta** state.  Because of the **Beta** state, things are in flux and are subject to change without warning.

# Requirements
The following must be installed in your Python

- [Python-Markdown 2.5.1+](https://pypi.python.org/pypi/Markdown)
- [Pygments 2.0 Dev branch](https://bitbucket.org/birkenfeld/pygments-main/overview)
- [PyYaml](http://pyyaml.org)

# Features
- Should work on Python 2.7 and 3.0+ compatible (but executables are currently built with Python 2.7 using Pyinstaller). Usually tested on Python 2.7 and Python 3.4.  Can only be compiled with Pyinstaller for Python 2.7.
- Should run on OSX, Windows, and Linux.  Usually tested on Windows and OSX though.
- Receive multiple files or file patterns to process.
- Receive input file stream for conversion.
- Configurable options file to tweak Python's Markdown package behavior.
- Uses Pygments for syntax highighlighting.
- Preview option to preview output in a browser.
- Parses yaml or json frontmatter.
- Optionally all the default Markdown extensions, plus these optional pymdown extensions:

    | Extension    | Description |
    |--------------|-------------|
    | caret        | Add <ins>insert</ins> by using `^^insert^^` and/or Pandoc style <sup>superscript</sub> by using `^superscript^`. Can be enabled in the settings file. |
    | tilde        | Add <del>delete</del> tags by using `~~delete~~` and/or Pandoc style <sub>subscript</sub> by using `~subscript~`.. Can be enabled in the settings file. |
    | mark         | Experimental extension to add <mark>mark</mark> by using `==mark==`. |
    | magiclink    | Search for and convert http or ftp links to actual HTML links for lazy link creation. Can be enabled in the settings file. |
    | htmlcomments | Remove html comments from the final output. |
    | tasklist     | This adds support for github style tasklists.  Can be enabled in the settings. |
    | githubemoji  | This adds emojis.  Assets link to github's emoji icons.  Can be enabled in the settings. |
    | headeranchor | Insert github style header anchor on left side of h1-h6 tags. |
    | progressbar  | Support for adding progress bars. |
    | betterem     | Better emphasis and strong support.  Defaults to using a *smart* configuration, but can be disabled for a *dumb* configuration. |
    | nestedfences | Allow the nesting of fences in blockquotes, lists, admonitions etc.  Can also disable support for indented code blocks. |
    | smartsymbols | Add support for auto convrting syntax for things like copyrite, trademark, registered, not equal, plus/minus, arrows, and selected fractions. |
    | github       | Adds `magiclink`, `betterem`, `tilde` (just delete), `githubemoji`, `tasklist`, `headeranchor`, and `nl2br` to get a github feel. It is advised to pair this with `extra`. |
    | pymdown      | Adds `magiclink`, `betterem`, `tilde`, `caret`, `githubemoji`, `tasklist`, `headeranchor`, `nl2br`, `smartsymbols`, `htmlcomments`, `nestedfences` and `progressbar`.  It is advised to pair this with `extra`. |
    | absolutepath | Converts local file paths from relative to absolute for things like links, images, etc.  This is automatically done on all previews.  It can be configured to run all the time outside of previews in the settings file, and it can take a hardcoded path `absolutepath(base_path=/my/path)` or a dynamic path `absolutepath(base_path=${BASE_PATH})` that can take the base_path fed in on the command line or calculated from the source files path.  If you set this in the settings file, keep in mind the settings file overrides preview's settings. |
    | b64          | Base64 encode local image files. If can be enabled and configured in the settings file and can take a hardcoded path `b64(base_path=/my/path)` or it can take a dynamic base_path `b64(base_path=${BASE_PATH})` fed in on the command line or calculated from the source files path. |

- Non-configurable extensions that extend PyMdowns abilities (cannot be set in the settings file):

    | Extension    | Description |
    |--------------|-------------|
    | critic       | It is configured automatically based on command line inputs.  In its current form, it can output in HTML a highlighted critic form to make it more readable.  If you select `--accept` or `--reject`, it will strip out the critic marks by accepting the changes or discarding them. |
    | plainhtml    | It is configured automatically based on command line inputs.  This extension strips out things like id's, styles etc. to give a more simple, plain HTML output. |

# Styles and Configuration
## Add More CSS and JS Files
Add them to the provided settings:

```javascript
    // Select your CSS for you output html
    // or you can have it all contained in your HTML template
    //
    // Is an array of stylesheets (path or link).
    // If it points to a physical file, it will be included.
    // PyMdown will look relative to the binary if it can't find the file.
    "css_style_sheets": ["default-markdown.css"],

    // Include the pygments css when using codehilite extension
    "use_pygments_css": true,

    // Load up js scripts
    //
    // Is an array of scripts (path or link).
    // If it points to a physical file, it will be included.
    // PyMdown will look relative to the binary if it can't find the file.
    "js_scripts": [],
```

## Syntax Highlighting with Pygments
Syntax highlighting can be done in fenced blocks when enabling the `codehilite` extension.  The styles etc. can be configured in the settings file as well. Here is an example:

```javascript
    "extensions": [
        "markdown.extensions.extra",
        "markdown.extensions.toc",
        "markdown.extensions.codehilite(guess_lang=False,pygments_style=tomorrownighteighties)"
    ]
```

Notice the syntax style is set with the `pygments_style` key.

If you don't want to use the sytles that are built-in and have your own pygments css file, you can disable the stylesheet generation, and just add your own.

```javascript
    // Select your CSS for you output html
    // or you can have it all contained in your HTML template
    //
    // Is an array of stylesheets (path or link).
    // If it points to a physical file, it will be included.
    // PyMdown will look relative to the binary if it can't find the file.
    "css_style_sheets": ["default-markdown.css", "my-pygments.css"],

    // Include the pygments css when using codehilite extension
    "use_pygments_css": false,
```

## Change the HTML Template
This can be done here:

```javascript
    // Your HTML template
    // PyMdown will look relative to the binary if it can't find the file.
    "html_template": "default-template.html",
```

Templates can use `{{ HEAD }}` to receive header info like CSS and JS files.  `{{ BODY }}` is used to receive markdown content. Optionally `{{ TITLE }}` i sused to receive the title.

## Advanced Custom Styles and Lexers
If you want your styles to work with codehilite's options of `noclasses`, your style will have to be compiled in. If you want custom lexers they have to be compiled in as well or Pygments won't be able to see or use them.  This is required because of the way Pygments uses external plugins, so the styles and lexers are bundled in an egg that defines its entry points properly.

Following Pygments guidelines for external styles and lexers, create your style or lexer and drop them in `pymdown-styles/pymdown_styles` and `pymdown-lexers/pymdown_lexers` respectively and update the `__init__.py` file for the respective plugin type.  After that you will need to update the respective `setup.py` with the entry point for your style/lexer.  Now you can build your eggs (with the python version you plan on using to run the tool):

```bash
python tools/gen_egg.py pydown-styles

python tools/gen_egg.py pydown-lexers
```

Some optional styles are already availble in `pymdown-styles`.

# Command Line

```
usage: pymdown [-h] [--version] [--licenses] [--quiet] [--preview]
               [--plain-html] [--title TITLE] [--accept | --reject]
               [--critic-dump] [--output OUTPUT] [--batch]
               [--settings SETTINGS] [--encoding ENCODING]
               [--basepath BASEPATH]
               [markdown [markdown ...]]

Markdown generator

positional arguments:
  markdown              Markdown file(s) or file pattern(s).

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --licenses            Display licenses.
  --quiet, -q           No messages on stdout.
  --preview, -p         Output to preview (temp file). --output will be
                        ignored.
  --plain-html, -P      Strip out CSS, style, ids, etc. Just show tags.
  --title TITLE         Title for HTML.
  --accept, -a          Accept propossed critic marks when using in normal
                        processing and --critic-dump processing
  --reject, -r          Reject propossed critic marks when using in normal
                        processing and --critic-dump processing
  --critic-dump         Process critic marks, dumps file(s), and exits.
  --output OUTPUT, -o OUTPUT
                        Output file. Ignored in batch mode.
  --batch, -b           Batch mode output.
  --settings SETTINGS, -s SETTINGS
                        Load the settings file from an alternate location.
  --encoding ENCODING, -e ENCODING
                        Encoding for input.
  --basepath BASEPATH   The basepath location pymdown should use.
```

# Sublime Plugin
A sublime plugin that utilizes this app is found here: [sublime-pymdown](https://github.com/facelessuser/sublime-pymdown)

# Credits
- Built on top of https://pypi.python.org/pypi/Markdown
- Uses the development branch of Pygments for Python 3 support http://pygments.org/.
- Includes optional Tomorrow Themes for Pygment from https://github.com/MozMorris/tomorrow-pygments
- Currently includes the original github theme and the newest 2014 variant.
- Inspiration for the project came from https://github.com/revolunet/sublimetext-markdown-preview.

# Build
Building is not required.  You can run the tool directly as uncompiled python scripts, but I usually build it in to portable binary.

- Download or clone Pyinstaller main branch (latest release won't work; the dev branch is needed) from github into the pymdown project folder https://github.com/pyinstaller/pyinstaller.  The whole thing should be copied in and the root folder should be renamed as pyinstaller.
- Optionally build the styles egg for your current python install if you want the github and tomorrow themes built in (use `tools/gen_egg.py pydown-styles`).
- Optionally add your custom lexers and build the egg for for the lexers for your current python install if you would like those lexers to be available (use `tools/gen_egg.py pydown-lexers`).
- Ensure that the [requirements](#requirements) are fullfilled.
- Using Python 2 run, `python build.py -c`
- Binary will be in the `pymdown/dist` folder

# TODO
- [ ] Better CSS in the default CSS file for print mode in webbrowsers
- [ ] Maybe add an extension for embedding content?
- [ ] Unit tests

Potentially anything else I haven't yet thought of.

# License
MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#3rd Party Licenses
See [licenses](https://github.com/facelessuser/PyMdown/blob/master/data/licenses.txt).
