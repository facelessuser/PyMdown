---
flow: true
sequence: true
---
[TOC]
# Overview
SuperFences provides 4 features:

1. The ability to nest fences under blockquotes, lists, or other block elements (this feature is provided as a workaround until a more official and better implementation is provided by the Python Markdown team; see [Limitations](#limitations) for more info).
2. Special UML flowchart fence via the `flow` language specifier.
3. Special UML sequence diagram via the `sequence` language specifier.
4. The ability to disable indented code blocks in favor of only using the fenced variant (off by default).

All features can be turned on or off.

## Nested Fenced Blocks
Fenced blocks requires all nested fence content to be at least at the indentation levels of the fences (blank lines excluded).  The opening and closing fence markers must be indented at the same level.  If you are using a fenced block inside a blockquote, at least the first line of the fenced block needs to have the appropriate number of `>` characters signifying the quote depth.

````
> ```
  a fenced block
  ```
````

Keep in mind that too many blank lines will cause a blockquote to terminate, so remember to use `>` markers accordingly if not marking every line.

````
> ```
  a fenced block

> with blank lines
  ```
````

If using a fenced block as the first line of a list, you will have to leave the first line blank, but remember that the list marker must be followed by a space.

````
-<space>
    ```
    a fenced block
    ```

Definition
:<space>
    ```
    a fenced block
    ```
````

## UML Diagrams
When using the UML diagram features, you must provide the necessary Javascript files for the HTML output.  The requirements are listed below:

**flowcharts:**

- [raphael.js](http://raphaeljs.com/)
- [flowchart.js](http://adrai.github.io/flowchart.js/)

**sequence diagrams:**

- [raphael.js](http://raphaeljs.com/)
- [underscore.js](http://underscorejs.org/)
- [sequece-diagram.js](http://bramp.github.io/js-sequence-diagrams/)


Simply including the libraries above is not enough as these libraries need to be pointed at the elements they need to convert.  If using the PyMdown application, and not just the extension, PyMdown provides a script `uml-loader.py` that can be used to target the HTML elements and execute the appropriate library on their content to create the desired diagrams.  `uml-loader.py` does not have to be used, and you can modify it or write your own to suite your needs; it is provided for convenience.

UML flowcharts and sequence diagrams will be rendered as HTML `<pre><code>` tags before the Javascript libraries are run on them.  They will be assigned CSS classes `uml-flowchart` and `uml-sequence-diagram` respectively for flowcharts and sequence diagrams.

# Limitations
This extension suffers from the same issues that the original fenced block extension suffers from.  Normally Python Markdown does not parse content inside HTML tags unless they are marked with the attribute `markdown='1'` etc.  But since this is run as a preprocessor, it is not aware of the HTML blocks.  So be aware of this.

SuperFences is made to work with the default extensions out of the box.  It will probably not work with other extensions such as Grid Tables since that extension allows for characters to obscure the blocks like blockquote syntax does (though this has been designed to work with blockquotes).  Ideally fenced blocks needs to be handled as a block parser, but there is much work to be done on Python Markdown's internal block handlers before this is possible.

SuperFences works best when following the guidelines.  If the guidelines are not followed, odd results may be encountered.

For the reasons above, the nested fences feature really is just a workaround.  But for a lot of people (including myself), this functionality is more than sufficient.

# Options

| Option    | Type | Default | Description |
|-----------|------|---------|-------------|
| disable_indented_code_blocks | bool | False | Disables Python Markdown's indented code block parsing.  This is nice if you only ever use fenced blocks. |
| nested | bool | True | Use nested fences. |
| uml_flow | bool | True | Enable flowcharts. |
| uml_sequence | bool | True | Enable sequence diagrams. |

# Examples
This highlights the special features of this extension except for `disable_indented_code_blocks`.

## Neseted Fences:

````
    ```
    This will still be parsed
    as a normal indented code block.
    ```

```
This will still be parsed
as a fenced code block.
```

- This is a list that contains multiple code blocks.

    - Here is an indented block

            ```
            This will still be parsed
            as a normal indented code block.
            ```

    - Here is a fenced code block:

        ```
        This will still be parsed
        as a fenced code block.
        ```

        > ```
        > Blockquotes?
        > Not a problem!
        > ```
````

    ```
    This will still be parsed
    as a normal indented code block.
    ```

```
This will still be parsed
as a fenced code block.
```

- This is a list that contains multiple code blocks.

    - Here is an indented block

            ```
            This will still be parsed
            as a normal indented code block.
            ```

    - Here is a fenced code block:

        ```
        This will still be parsed
        as a fenced code block.
        ```

        > ```
        > Blockquotes?
        > Not a problem!
        > ```

## UML Flow Charts
````
```flow
st=>start: Start:>http://www.google.com[blank]
e=>end:>http://www.google.com
op1=>operation: My Operation
sub1=>subroutine: My Subroutine
cond=>condition: Yes
or No?:>http://www.google.com
io=>inputoutput: catch something...

st->op1->cond
cond(yes)->io->e
cond(no)->sub1(right)->op1
```
````

```flow
st=>start: Start:>http://www.google.com[blank]
e=>end:>http://www.google.com
op1=>operation: My Operation
sub1=>subroutine: My Subroutine
cond=>condition: Yes
or No?:>http://www.google.com
io=>inputoutput: catch something...

st->op1->cond
cond(yes)->io->e
cond(no)->sub1(right)->op1
```

## UML Sequence Diagrams
````
```sequence
Title: Here is a title
A->B: Normal line
B-->C: Dashed line
C->>D: Open arrow
D-->>A: Dashed open arrow
```
````

```sequence
Title: Here is a title
A->B: Normal line
B-->C: Dashed line
C->>D: Open arrow
D-->>A: Dashed open arrow
```
