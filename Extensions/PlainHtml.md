[TOC]
# Overview
PlainHtml is a simple extension that is run at the end of post-processing.  It searches the final output stripping things like `style`, `id`, `class`, and `on<name>` attributes from HTML tags.  It also removes HTML comments.  If you have no desire to see these, this can strip them out.  Though it does its best to be loaded at the very end of the process, it helps to include this one last when loading up your extensions.

!!! Caution "Warning"
    This is not meant to be a sanitizer for HTML.  This is just meant to try and strip out style, script, classes, etc. to provide a plain HTML output for the times this is desired; this is not meant as a security extension.  If you want something to secure the output, you should consider running a sanitizer like [bleach](https://pypi.python.org/pypi/bleach).
