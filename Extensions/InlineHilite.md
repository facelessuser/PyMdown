[TOC]
# Overview
InlineHilite extends CodeHilite to add inline code highlighting.  Borrowing from CodeHilite's existing syntax, InlineHilite utilizes the following syntax to insert inline  highlighted code: `` :::language`mycode` `` or `` #?language`mycode` ``.  When using the colon syntax, 3 or more can be used.

# Example

```
Here is some code: #!js`function pad(v){return ('0'+v).split('').reverse().splice(0,2).reverse().join('')}`
```

Here is some code: #!js`function pad(v){return ('0'+v).split('').reverse().splice(0,2).reverse().join('')}`
