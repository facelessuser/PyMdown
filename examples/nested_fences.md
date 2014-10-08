Paragraph with words

```
Normal fenced block

Still works
```

Indented block

    ```javascript
    // Fenced **with** highlighting

    function doIt() {
        for (var i = 1; i <= slen ; i^^) {
            setTimeout("document.z.textdisplay.value = newMake()", i*300);
            setTimeout("window.status = newMake()", i*300);
        }
    }
    ```


!!! danger "admonition"
    Some words

    - Level 1 List

        ```javascript
        // Fenced **with** highlighting

        function doIt() {
            for (var i = 1; i <= slen ; i^^) {
                setTimeout("document.z.textdisplay.value = newMake()", i*300);
                setTimeout("window.status = newMake()", i*300);
            }
        }
        ```

        - test

            ```javascript
            // Fenced **with** highlighting

            function doIt() {
                for (var i = 1; i <= slen ; i^^) {
                    setTimeout("document.z.textdisplay.value = newMake()", i*300);
                    setTimeout("window.status = newMake()", i*300);
                }
            }
            ```

            ```
          Unaligned content
            ```

    !!! danger "sub admonition"
        Testing

        - test

            ```javascript
            // Fenced **with** highlighting

            function doIt() {
                for (var i = 1; i <= slen ; i^^) {
                    setTimeout("document.z.textdisplay.value = newMake()", i*300);
                    setTimeout("window.status = newMake()", i*300);
                }
            }
            ```

            - test

                Indented code block

                    ```javascript
                    // Fenced **with** highlighting

                    function doIt() {
                        for (var i = 1; i <= slen ; i^^) {
                            setTimeout("document.z.textdisplay.value = newMake()", i*300);
                            setTimeout("window.status = newMake()", i*300);
                        }
                    }
                    ```

                ```
              Unaligned text
                ```

    A blockquote
    > A quote
    >
    > - list
    >       some words
    >       some more words
    >
    >       - sub list
    >
    >           ```python
    >           a = re.compile(r"""\d +  # the integral part
    >              \.    # the decimal point
    >              \d *  # some fractional digits""", re.X)
    >           b = re.compile(r"\d+\.\d*")
    >           ```

    >
    >  > Sub blockquote with spaced out text
    >  > ```python
    >  > def displaymatch(match):
    >
    >  >     if match is None:

    >

    >  >         return None
    >  > return '<Match: %r, groups=%r>' % (match.group(), match.groups())
    >  > ```
    >
