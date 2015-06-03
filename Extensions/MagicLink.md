---
use_template: true
references:
  - _references/references.md
---
[TOC]
# Overview
GFM has a nice feature that detects and auto-generates links.  This extension adds similar functionality to Python Markdown allowing you to just type or paste links; no special syntax required.  It auto-links html, ftp, and email links.

# Examples

```
This requires no special syntax.

Just paste links directly in the document like this: https://github.com/facelessuser/PyMdown.

Or even an email address fake.email@email.com.
```

This requires no special syntax.

Just paste links directly in the document like this: https://github.com/facelessuser/PyMdown.

Or even an email address fake.email@email.com.

{{ extra.references|gettxt }}
