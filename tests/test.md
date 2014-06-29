# Cheat Sheet and Test

## Headers

```
# H1
## H2
## H3
### H4
#### H5
##### H6
```

# H1
## H2
## H3
### H4
#### H5
##### H6

## Paragraphs
```
This is a paragraph.
I am still part of the paragraph.

New paragraph.
```

This is a paragraph.
I am still part of the paragraph.

New paragraph.

## Inline

```
**bold** and __bold 2__

*italic*  and _italic 2_

***bold and italic*** ___bold and italic 2__  __*bold and italic 3*__ **_bold and italic 4_**
```

**bold** and __bold 2__

*italic*  and _italic 2_

***bold and italic*** ___bold and italic 2___  __*bold and italic 3*__ **_bold and italic 4_**

## Links
```
![Some Picture](bj.png "Some Picture")

[Link](bg.png "Link")
```

![Base 64 encoded image](bg.png "Some Picture")

[Link](bg.png "Link")

## Lists

```
List

- item 1
- item 2
- item 3

List 2

* item 1
* item 2
* item 3

List 3

+ item 1
+ item 2
+ item 3

Ordered List

1. item 1
2. item 2
3. item3


Dictionary
: item 1

  item 2

  item 3
```

List

- item 1
- item 2
- item 3

List 2

* item 1
* item 2
* item 3

List 3

+ item 1
+ item 2
+ item 3

Ordered List

1. item 1
2. item 2
3. item 3

Dictionary
:   item 1

    item 2

    item 3

## Blocks
```
`inline block`

    This is a block
    
    This is more of a block

```

`inline block`

    This is a block
    
    This is more of a block


## Fenced Block
```
// Fenced **without** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i++) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```


```javascript
// Fenced **with** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i++) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```

# Test Extensions

## Delete
```
~~strike~~

~~*strike italic*~~  *~~strike italic 2~~*

~~_strike italic_~~  _~~strike italic 2~~_

~~**strike bold**~~  **~~strike bold 2~~**

~~__strike bold__~~  __~~strike bold 2~~__

~~***strike italic bold***~~  ***~~strike italic bold 2~~***

~~___strike italic bold___~~  ___~~strike italic bold 2~~___

**~~*strike italic bold*~~**  *~~**strike italic bold 2**~~*

__~~_strike italic bold_~~__  _~~__strike italic bold 2__~~_

**~~_strike italic bold_~~**  _~~**strike italic bold 2**~~_

__~~*strike italic bold*~~__  *~~__strike italic bold 2__~~*
```

~~strike~~

~~*strike italic*~~  *~~strike italic 2~~*

~~_strike italic_~~  _~~strike italic 2~~_

~~**strike bold**~~  **~~strike bold 2~~**

~~__strike bold__~~  __~~strike bold 2~~__

~~***strike italic bold***~~  ***~~strike italic bold 2~~***

~~___strike italic bold___~~  ___~~strike italic bold 2~~___

**~~*strike italic bold*~~**  *~~**strike italic bold 2**~~*

__~~_strike italic bold_~~__  _~~__strike italic bold 2__~~_

**~~_strike italic bold_~~**  _~~**strike italic bold 2**~~_

__~~*strike italic bold*~~__  *~~__strike italic bold 2__~~*

## Insert
```
++insert++

++*insert italic*++  *++insert italic 2++*

++_insert italic_++  _++insert italic 2++_

++**insert bold**++  **++insert bold 2++**

++__insert bold__++  __++insert bold 2++__

++***insert italic bold***++  ***++insert italic bold 2++***

++___insert italic bold___++  ___++insert italic bold 2++___

**++*insert italic bold*++**  *++**insert italic bold 2**++*

__++_insert italic bold_++__  _++__insert italic bold 2__++_

**++_insert italic bold_++**  _++**insert italic bold 2**++_

__++*insert italic bold*++__  *++__insert italic bold 2__++*
```

++insert++

++*insert italic*++  *++insert italic 2++*

++_insert italic_++  _++insert italic 2++_

++**insert bold**++  **++insert bold 2++**

++__insert bold__++  __++insert bold 2++__

++***insert italic bold***++  ***++insert italic bold 2++***

++___insert italic bold___++  ___++insert italic bold 2++___

**++*insert italic bold*++**  *++**insert italic bold 2**++*

__++_insert italic bold_++__  _++__insert italic bold 2__++_

**++_insert italic bold_++**  _++**insert italic bold 2**++_

__++*insert italic bold*++__  *++__insert italic bold 2__++*


## Magiclinks

https://github.com/facelessuser/BracketHighlighter/tree/ST3

This is a link https://github.com/facelessuser/BracketHighlighter/tree/ST3.

This is a link "https://github.com/facelessuser/BracketHighlighter/tree/ST3".

With this link (https://github.com/facelessuser/BracketHighlighter/tree/ST3), it still works.


## Base64
Image should be embedded in base 64 below:
```
![Some Picture](bj.png "Some Picture")
```

![Base 64 encoded image](bg.png "It works!")


## Absolutepath
Should convert bg.png to the actual full path below:
```
[Absolute path link](bg.png "It works!")
```

[Absolute path link](bg.png "It works!")
