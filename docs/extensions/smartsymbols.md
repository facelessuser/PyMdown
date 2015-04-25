# SmartSymbols {: .doctitle}
Auto-convert special symbols.
{: .doctitle-info}

---

# Overview
SmartSymbols adds syntax for creating special characters such as trademarks, arrows, fractions, etc.  It basically allows for more "smarty-pants" type replacements.  It is meant to be used along side the Python Markdown's `smarty` extension.

# Options
| Option          |  Description |
|-----------------|--------------|
| trademark       | Add syntax for tradmark symbol.   |
| copyright       | Add syntax for copyright symbol.  |
| registered      | Add syntax for registered symbol. |
| care_of         | Add syntax for care / of.         |
| plusminus       | Add syntax for plus / minus.      |
| arrows          | Add syntax for creating arrows.   |
| notequal        | Add syntax for not equal symbol.  |
| fractions       | Add syntax for common fractions.  |
| ordinal_numbers | Add syntax for ordinal numbers.   |

# Examples

| Markdown      | Result     |
|---------------|------------|
| `(tm)`        | (tm)       |
| `(c)`         | (c)        |
| `(r)`         | (r)        |
| `c/o`         | c/o        |
| `+/-`         | +/-        |
| `-->`         | -->        |
| `<--`         | <--        |
| `<-->`        | <-->       |
| `!=`          | !=         |
| `1/4, etc.`   | 1/4, etc.  |
| `1st 2nd etc.`|1st 2nd etc.|
