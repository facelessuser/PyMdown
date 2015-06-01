# Github {: .doctitle}
Simulation of Github Flavored Markdown.

---

## Overview
The Github extension is a convenience extension to load up and configure the minimum extensions needed to get a GFM feel.  It is not a 1:1 emulation, but some aspects are pretty close.  I don't really have a desire to to make it exact, but the feel is nice if you like GFM feel; some things may differ slightly.

!!! Caution "Reminder"
    Be mindful of which extensions are being loaded here.  If you load `pymdown.github` and `markdown.extensions.extra`, you will be loading some extensions multiple times.

    You will also need to load the `markdown.extensions.codehilite` extension yourself as well with `guess_lang=False` and your preferred Pygments style (if available) or use some other JavaScript highlighter.  Though there is no Github style included with the extension, the PyModwn tool comes with the original Pygments Github style (github) and the Github 2014 style (github2014) which they Github used before they ditched Pygments for their own in-house highlighter.

Extensions that get loaded:

| Extension | Options | Name   |
|-----------|---------|--------|
| [Tables](https://pythonhosted.org/Markdown/extensions/tables.html) | | markdown.extensions.tables |
| [New&nbsp;Line&nbsp;to&nbsp;Break](https://pythonhosted.org/Markdown/extensions/nl2br.html) | | markdown.extensions.nl2b |
| [magiclink](./magiclink.md)      | | pymdownx.magiclink |
| [betterem](./betterem.md)        | | pymdownx.betterem |
| [tilde](./tilde.md)              | `#!python {"subscript": False}` | pymdownx.tilde |
| [githubemoji](./githubemoji.md)  | | pymdownx.githubemoji |
| [tasklist](./tasklist.md) | | pymdownx.tasklist |
| [headeranchor](./headeranchor.md)| | pymdownx.headeranchor |
| [superfences](./superfences.md) | | pymdownx.superfences |

*[GFM]:  Github Flavored Markdown
