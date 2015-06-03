---
use_template: true
references:
  - _references/references.md
---
[TOC]
# Overview
The Github extension is a convenience extension to load up and configure the minimum extensions needed to get a GFM feel.  It is not a 1:1 emulation, but some aspects are pretty close.  I don't really have a desire to to make it exact, but the feel is nice if you like GFM feel; some things may differ slightly.

!!! Caution "Reminder"
    Be mindful of which extensions are being loaded here.  If you load `pymdown.github` and `markdown.extensions.extra`, you will be loading some extensions multiple times.

    You will also need to load the `markdown.extensions.codehilite` extension yourself as well with `guess_lang=False` and your preferred Pygments style (if available) or use some other Javascript highlighter.  Though there is no github style included with the extension, the PyModwn tool comes with the original Pygments github style (github) and the github 2014 style (github2014) which they Github used before they ditched Pygments for their own in-house highlighter.

Extensions that get loaded:

- markdown.extensions.tables
- markdown.extensions.nl2b
- pymdown.magiclink
- pymdown.betterem
- pymdown.tilde(subscript=False)
- pymdown.githubemoji
- pymdown.tasklist
- pymdown.headeranchor
- pymdown.superfences

{{ extra.references|gettxt }}
