[TOC]
# Overview
InlineHilite extends CodeHilite to add inline code highlighting.  Borrowing from CodeHilite's existing syntax, InlineHilite utilizes the following syntax to insert inline  highlighted code: `` `:::language mycode` `` or `` `#!language mycode` ``.  We will call these specifiers mock shebangs.

When using the colon mock shebang, 3 or more colons can be used.  Mock shebangs must come **immediately** after the opening backtick(s) and must be followed by at least one space.  If you need to escape a mock shebang at the start of a code block, just put a space before it and it will be treated as part of the code.

# Options

InlineHilite has no options, but it relies on Codehilite and its options.  The idea is that InlineHilite extends Codehilite.  So InlineHilite only works when Codehilite is enabled, and it uses the same options that Codehilite uses; namely: `guess_lang`, `css_class`, `pygments_style`, `use_pygments`.

# Example

```
Here is some code: `#!js function pad(v){return ('0'+v).split('').reverse().splice(0,2).reverse().join('')}`.

The mock shebang will be treated like text here: ` #!js var test = 0; `.
```

Here is some code: `#!js function pad(v){return ('0'+v).split('').reverse().splice(0,2).reverse().join('')}`

The mock shebang will be treated like text here: ` #!js var test = 0; `.
