# General Usage

## Using PyMdown

PyMdown was written to aid in batch processing Markdown files with Python Markdown and Pygments (but a JavaScript highlighter can just as easily be used).  It also adds a number of optional extensions.

PyMdown can also optionally use a template with CSS and JavaScript for styling the Markdown outputs.  Templates, CSS, JavaScript, and extensions are all setup in a configuration file.  If for certain batches specific settings need to be tweaked, PyMdown can accept paths to specific settings file via the CLI.  The settings files is in the YAML format.  PyMdown also supports input sources with a YAML frontmatter where settings can be configured along with general meta data.

Though PyMdown could be used to generate a site, it was mainly designed to generate static documents from Markdown for general use or previewing.  If you are looking to generate document sites, there are plenty of good tools that already do this ([mkdocs][mkdocs] is one suggestion).  But even if you don't directly use PyMdown, you may still find the [PyMdown extensions][pymdownx] as useful additions in other Python Markdown related projects as they can be installed and used independently.

## Command Line Interface

### Input Files

In its most basic usage, PyMdown accepts a markdown file:

```bash
pymdown file.md
```

or a file stream:

```bash
pymdown < file.md
```

### Specifying Output

PyMdown allows the output to be specified with the `--output` or `-o` option:

```bash
pymdown -o file.html file.md
```

Alternatively you can redirect the output:

```bash
pymdown file.md > file.html
```

### Batch Processing

PyMdown has a batch processing mode (`--batch` or `-b`). When the batch flag is set, PyMdown will accept multiple paths and wild-card patterns.

```bash
pymdown -b *.md documents/*md
```

When in batch mode, PyMdown will simply transform the input file name: `file.md` -> `file.html`. It will then save the output file in the same location as the input.

### Previewing Markdown

With the `--preview` or `-p` option, PyMdown will generate a temp HTML file and open it in the default web browser.  Preview mode will work in normal and batch mode.

```bash
pymdown -p file.md
```

### Basepath

PyMdown in various circumstances (particularly in conjunction with specific PyMdown extensions) will try and resolve image, CSS, and JS asset paths for previews, base64 encoding, and other scenarios.  In order for this to work, a base path may be required and can be specified using the `--basepath` option.  If no base path is given, the base path will be that of the source file or `None` if the source is a file stream.

```bash
pymdown --basepath ../assets file.md
```

### Relpath

PyMdown in various circumstances (particularly in conjunction with specific PyMdown extensions) will try to create relative paths to assets or sources such as images, CSS, and JS.  In order for this to work, a relative path is needed.  The `--relpath` option is used to set this.  If `--relpath` is not set, it defaults to the output directory.  If the output directory is also not set (when output is dumped to stdout), the relative path will not be set.

```bash
pymdown --relpath ../somedirectory file.md
```

### Settings

PyMdown will normally look in the location of the [configuration directory](#configuration-file) to find the settings file, but the filename and path can be redirected with the `--settings` or `-s` option.

```bash
pymdown -s ../my_settings.yml file.md
```

### Encoding

PyMdown can be configured to read the Markdown file(s) with a different encoding than the default `UTF-8`.  This is done with the `--encoding` or `-e` option.

```bash
pymdown -e utf-8 file.md
```

By default, the output encoding will be the same as the input, but if greater control is needed, the user can set the output encoding via the `--output_encoding` or `-E` option.

```bash
pymdown -E utf-8 file.md
```

### Title

PyMdown, by default, will use the source file's name as the title, or if the input is a file stream, it will use **Untitled**.  But this can be set/overridden with the `--title` option.  This probably isn't practical for batch processing.  When batch processing, it may make more sense to utilize the [frontmatter](#frontmatter) to set the title per file.

```bash
pymdown --title "My Awesome File" file.md
```

### Critic

PyMdown has a couple options from CriticMarkup.  By using the `--accept` or `-a` option, when the Markdown is parsed, the suggested changes will be accepted.

When using the `--reject` or `-r` option when Markdown is parsed, the suggested changes will be rejected and the original content will be used instead.

If both `--accept` and `--reject` are set at the same time, PyMdown will use the view mode and convert the file to HTML and will attempt to highlight the blocks targeted with the CriticMarkup.

Lastly, the `--critic-dump` option, when used with either the `--accept` or `--reject` option, will take the source and output it accepting or rejecting respectively the CriticMarkup edits that were made (essentially removing the CriticMarkup from the file).

### Plain HTML

If a stripped down HTML output is preferred, the `--plain-html` or `-P` option will return a stripped down output with no templates, no HTML comments, and no id, style, class, or on* attributes.

```bash
pymdown -P file.md
```

### Force No Template

If by default the configuration file has defined a template, but it is desired to do an output without the template, the `--force-no-template` option can be used to disable template use.

```bash
pymdown --force-no-template file.md
```

### Force Stdout

Sometimes a file may have frontmatter that redirects its output to a file, but it may be desirable to send the output to stdout.  In this case, the `--force-stdout` option can be used to force a redirect to stdout.

```bash
pymdown --force-stdout file.md
```

### Quiet
In some situations it may be desired to hide error messages and general info from the stdout.  In this case, the `--quiet` or `-q` option may be used.

```bash
pymdown -q file.md
```

## Configuration File

The configuration file is used to specify general Python Markdown settings, optional template, CSS and JS resources for templates, and extensions that will be used.

PyMdown on the first run will unpack user files to `~\.PyMdown` on Windows, `~/.PyMdown` on OSX and `~/.config/PyMdown` on Linux.  The global configuration file can found here at the root of the folder along with default CSS, JavaScript, and other resources which would be under another sub-folder called `default`.  Files under `default` will be auto-upgraded when necessary by newer versions of PyMdown and should be left unaltered.  Default files can be copied and altered outside of the `default` location for personal tweaking and usage.

### Python Markdown Settings

Python Markdown has a number of settings that can be configured:

```yaml
# Length of tabs in source files
tab_length: 4

# Output format (html|xhtml)
# It is recommend to use more specific versions such as: html5 or xhtml1 than
# general html or xhtml
output_format: 'xhtml1'
```

Safe mode setting is omitted as it is pending deprecation in Python Markdown.

### Pygment Settings

The `use_pygments_css` setting controls whether Pygments CSS will be injected in the HTML output for code blocks. This can be turned off if you are applying your own, or if you are configured to use a JavaScript syntax highlighter.

```yaml
# Include the pygments css for code highlight blocks.
use_pygments_css: true,
```

This will inject Pygments CSS only if Pygments is installed, and will inject it even if you configure your extensions to not use Pygments.

This `pygments_style` setting is used to configure which installed Pygments theme PyMdown should insert into your HTML template.

```yaml
# Name of installed Pygments style to use.
pygments_style: default
```

Lastly, `pygments_class` determines what class will be prepended to all of the Pygment's CSS theme rules.

```yaml
# Pygments class to use.  This applies a class to the Pygments CSS
# so that only elements with the class below will be syntax highlighted.
# If using this, make sure you've configured CodeHilite and/or InlineHilite
# to use the same name.
pygments_class: highlight
```

!!! tip "Tip"
    If you want to use a JavaScript highlighter such as [highlight.js][highlightjs], you should disable `use_pygments_css`, and set `use_pygments` to `False` in CodeHilite, Highlight and/or InlineHilite.

### Template

PyMdown allows for specifying a simple HTML template that can be used for the output.  Template files can be specified in the settings file via the `template` keyword.

```yaml
# Your HTML template
# PyMdown will look relative to the binary if it can't find the file.
template: default/template.html
```

Template files in the settings or frontmatter can be followed by `;encoding` to cause the file to be opened and read with the specified encoding.

The template file uses Jinja2 to handle template variables.  Please see [Templating](#templating) for more info on how to access page data in a template.

### Javascript and CSS

Javascript and CSS can be included in the template by adding them to the following arrays:

```yaml
# Select your CSS for you output html
# or you can have it all contained in your HTML template
#
# Is an array of stylesheets (path or link).
# If it points to a physical file, it will be included.
# PyMdown will look relative to the binary if it can't find the file.
#
# This can be overridden in a file's frontmatter via the 'settings' key word:
#
# ---
# pymdown_settings:
#   css:
#     - somefile.css
# ---
#
# but if you want to append to the list, you can use just the 'css' keyword in the
# frontmatter:
#
# ---
# css:
#   - somefile.css
# ---
#
css:
- ^default/markdown.css

# Load up js scripts (in head)
#
# Is an array of scripts (path or link).
# If it points to a physical file, it will be included.
# PyMdown will look relative to the binary if it can't find the file.
#
# This can be overridden in a file's frontmatter via the 'pymdown_settings' key word:
#
# ---
# pymdown_settings:
#   js:
#     - somefile.js
# ---
#
# but if you want to append to the list, you can use just the 'js' keyword in the
# frontmatter:
#
# ---
# js:
#   - somefile.js
# ---
#
js: []
```

CSS files and JavaScript files can be URLs or file paths.  When specifying a file path, a `!` can be used to precede the path so that PyMdown will just link the file and skip converting the file to an absolute or relative path.  If the file path is preceded by a `^`, the file content will be embedded in the HTML under a style or script tag depending on the source type.

CSS and JavaScript files can also be followed by `;encoding` to read in the file with the specified encoding.

### Enabling Jinja2 Templating in Markdown Content

If desired, Jinja2 templating can be enabled in Markdown content.  While Jinja2 usage in Markdown content can be enabled globally, it is recommended to enable it in specific pages via the YAML frontmatter.

```yaml
# Enable Jinja2 Template support inside of Markdown content
use_jinja2: false
```

You can also control the tag style if you find the default difficult to use within your content either globally in your settings file, or in your page's YAML frontmatter.

```yaml
# By default, Jinja2 uses {% block %} for blocks. You can change that here
# or change it per file in your frontmatter. Only affects Markdown content template tags.
jinja2_block: ['{%', '%}']

# By default, Jinja2 uses {{ variable }} for variables. You can change that here
# or change it per file in your frontmatter. Only affects Markdown content template tags.
jinja2_variable: ['{{', '}}']

# By default, Jinja2 uses {# comment #} for comments. You can change that here
# or change it per file in your frontmatter. Only affects Markdown content template tags.
jinja2_comment: ['{#', '#}']
```

See [Templating](#templating) to learn more about accessing these template variables.

### Path Conversions

By default, PyMdown converts paths to be relative to the output location.  If desired, this can be changed to an absolute path:

```yaml
# By default resource paths are converted to relative file paths when possible;
# this disables conversion.
path_conversion_absolute: false
```

If path conversion is not wanted, and disabling the conversion inline with the `!` token is not acceptable, path conversion can be completely disabled with the following setting:

```yaml
# By default resource paths are converted to relative file paths when possible;
# this disables conversion.  Previews will still convert paths to render preview proper.
disable_path_conversion: false
```

!!! caution "Note"
    PyMdown utilizes the [pathconverter][pathconverter] extension to convert links and references in the actual markdown content.  If `pathconverter` is manually configured instead of letting PyMdown handle it, these settings will have no effect.

    The other exception is with previews.  In order for links and references to work in previews, they must be paths that are relative to the preview's temp directory or they must be absolute paths.  For this reason, PyMdown will always enable path conversions for previews.  If you have manually set up the `pathconverter` extension, preview's will overwrite the `relative_path` argument to ensure it is set to `${OUTPUT}` which will allow the preview to display content properly by making asset paths relative to the previews location.  By default, the `relative_path` is set to `${REL_PATH}` which is the output path by default, but can be altered via the command line option `--relpath` or the `relpath` frontmatter option.

### Python Markdown Extensions

Extensions to be used are defined under the **markdown_extensions** keyword.  **markdown_extensions** is an ordered key/value pair. An extension has a name followed by `:` in yaml format.  If you want to include settings parameters, you can include those as the extension value.  All parameters should be done as key/value pairs as shown below.

```yaml
markdown_extensions:
  markdown.extensions.extra:
  markdown.extensions.toc:
    title: Table of Contents
    slugify: !!python/name:pymdownx.headeranchor.uslugify
  markdown.extensions.codehilite:
    guess_lang: false
  markdown.extensions.smarty:
  markdown.extensions.wikilinks:
  markdown.extensions.admonition:
  markdown.extensions.nl2br:
  pymdown.pymdown:
  pymdown.b64:
    base_path: ${BASE_PATH}
  pymdown.critic:
```

There are a couple of special variables you can use in extension settings:

Name           | Description
-------------- | -----------
`${BASE_PATH}` | Insert the base path from command line or frontmatter.
`${REL_PATH}`  | Insert the relative path from command line or frontmatter.
`${OUTPUT}`    | Insert the output path (or destination) from command line or frontmatter.

## Frontmatter

Frontmatter can be used at the very beginning of a Markdown file.  Frontmatter blocks begin with `---` and end with `---`.  Frontmatter must be the very beginning of the file and start on the very first line.

PyMdown frontmatter content must be in the YAML format.  The frontmatter is a dictionary of key value pairs which will either be available in templates and/or used to set some functionality or setting per page.

```md
---
title: My Title
author: My Name
etc: You get the idea
---
### Markdown Header

Markdown content.
```

PyMdown has a few special keywords that can be defined to alter the output.  All other keys will be counted as user variables.

Keyword            | Description
------------------ | -----------
`title`            | This item is used in the HTML's title tag.
`destination`      | This keyword is the location and file name were the output should be placed.
`basepath`         | This is used to specify the path that PyMdown should use to look for reference material like CSS or JS files and even `references` defined in the frontmatter. It is also used in plugins such as `pathconverter` and `b64`.  This can override the `basepath` fed in at the command line.
`relpath`          | This is used to specify the path that images and paths are relative to. It is used in plugins such as `pathconverter`.  This can override the `relpath` fed in at the command line.
`css`              | This keyword's value is an array of strings denoting additional single CSS files to include.  They follow the same convention as CSS defined in the settings file: `;encoding` at tail will define the encoding used to access the file, paths starting with `!` will not have their path converted to absolute or relative paths, and `^` will directly embed the content in the HTML file.
`js`               | This keyword's value is an array of strings denoting additional single JavaScript files to include.  They follow the same convention as JavaScript defined in the settings file: `;encoding` at tail will define the encoding used to access the file, paths starting with `!` will not have their path converted to absolute or relative paths, and `^` will directly embed the content in the HTML file.
`pymdown_settings` | This is a dictionary and allows the overriding of any of the settings found in the original configuration file.

See [Templating](#templating) to learn more about accessing these values in your HTML template.

### Custom Frontmatter

If the keyword is not one of the special keywords defined above, they will automatically be available in the template variables under `extra`

## Templating

Templates are HTML files that use [Jinja2][jinja2] templating syntax.  Template variables and logic is used in the HTML templates.  If desired, Jinja2 templating can be enabled in the Markdown content by with the following syntax:

```yaml
pymdown_settings:
  use_jinja2
```

It is up to the user to escape content that must be escaped. If desired, the brackets for a given page can be changed with the following frontmatter:

```yaml
pymdown_settings:
  jinja2_block: ['{%', '%}']
  jinja2_variable: ['{{', '}}']
  jinja2_comment: ['{#', '#}']
```

Template data is found under three variables:

Variable   | Description
---------- |------------
`page`     | Data related to the specific page.
`extra`    | This contains user defined variables.  These can come from the settings file under the `extra` keyword, or any non-default keyword found in the frontmatter. Extra can contain any content and structure the user specifies.
`settings` | This is the the settings used for the page.  It contains the merged state of the settings from the settings file and frontmatter.  The values will also contained final adjusted states if any had to be made.

### Page Variables

The page variable contains the page specific variables.

Variables             | Description
--------------------- |------------
`page.title`          | The title for the page (escaped).
`page.encoding`       | The specified encoding for the HTML page.
`page.content`        | The HTML content from the markdown source.
`page.js`             | An array of JavaScript files or links that were specified to be include.  File paths may contain special markers such as `^` and `!` at the beginning to specify to embed the content directly or not to convert path respectively. File paths may also include encoding specifiers at the end in the form `;encoding`. Special [template filters](#template-filters) have been provided to process these files and links and return either the links or contents as intended. Returns will be wrapped in their appropriate tags.
`page.css`            | An array of CSS files or links that were specified to be include.  File paths may contain special markers such as `^` and `!` at the beginning to specify to embed the content directly or not to convert path respectively. File paths may also include encoding specifiers at the end in the form `;encoding`. Special [template filters](#template-filters) have been provided to process these files and links and return either the links or contents as intended. Returns will be wrapped in their appropriate tags.
`page.basepath`       | Basepath used as a reference point to find other files.
`page.relpath`        | Relative path that the page may have used to calculate paths for links etc.
`page.destination`    | The output location for the file.
`page.pygments_style` | Will contain the Pygments style CSS content to embed in the page. If this option has been disabled for any reason, it will be null.

### Template Filters

The template environment contains all the normal default Jinja2 filters and a couple of extras.

#### Embedding Images

`#!py3 embedimage(image_path)`
: 

    Given the path, embed the image directly into the HTML with base64 encoding.  Image paths are resolved relative to the base path.

    **Example**

    ```jinja
    {{ path/to/image.png|embedimage }}
    ```

#### Get CSS

`#!py3 getcss([files])`
: 

    Given a single file or array of files, resolve the file path and either embed the content of the file(s) or provide a link(s) as specified in the settings, frontmatter, or inline with appropriate PyMdown notation.

    **Example**

    ```jinja
    {# Include css link #}
    {{ page.css|getcss }}
    ```

    ```jinja
    {# Do not convert path for CSS link #}
    {{ '!path/to/css/file.css'|getcss }}
    ```

    ```jinja
    {# Embed file content #}
    {{ '^path/to/css/file.css'|getcss }}
    ```

#### Get JavaScript

`#!py3 getjs([files])`
: 

    Given a single file or array of files, resolve the file path and either embed the content of the file(s) or provide a link(s) as specified in the settings, frontmatter, or inline with appropriate PyMdown notation.

    **Example**

    ```jinja
    {# Include JS link #}
    {{ page.js|getjs }}
    ```

    ```jinja
    {# Do not convert path for JS link #}
    {{ '!path/to/js/file.js;utf-8'|getjs }}
    ```

    ```jinja
    {# Embed file content #}
    {{ '^path/to/js/file.js;utf-8'|getjs }}
    ```

#### Get Text

`#!py3 gettxt([files])`
: 

    Given a single file or array of files, resolve the file path and embed the content of the file(s).

    **Example**

    ```jinja
    {# Embed text content #}
    {{ 'some/path/to.txt'|gettxt }}
    ```

#### Get Path

`#!py3 getpath(path)`
: 

    Given a path, adjust with internal base path and relative path settings to return the desired path.

    **Example**

    ```jinja
    {{ 'path/to/something'|getpath}}
    ```

#### Get Path URL

`#!py3 getpathurl(path)`
: 

    Given a path, adjust with the internal base path and relative path settings to return the desired path, but also encode it for a URL; path will be quoted (quotes converted for placement in an HTML attribute).

    **Example**

    ```html+jinja
    <img src="{{ 'assets/some/image.png'|getpathurl }}"/>
    ```

#### Get Meta

`#!py3 getmeta(value, name='name')`
: 

    Given the value and name, return a simple meta tag: `#!html <meta name="name" value="value">`.  `value` can be either a single string or array of strings; if an array, the values will be joined with `, `.

    **Example**

    ```jinja
    {{ extra.author|getmeta(name='author') }}
    ```

--8<-- "refs.md"
