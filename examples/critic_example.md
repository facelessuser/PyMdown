{--# Cheat Sheet and Test

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
--}
## Paragraphs
```
This is a paragraph.
I am still part of the paragraph.

New paragraph.
```

{++This is a paragraph.
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

## Links++}
```
![Image](bj.png "Some Picture")

[Link](bg.png "Link")
```

![Image](bg.png "Some Picture")

[Link](bg.png "Link")

{~~## Um... maybe Lists~>## Lists~~}

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

{==## Blocks
```
`inline block`

    This is a block
    
    This is more of a block

```

`inline block`

    This is a block
    
    This is more of a block==}{>>I like this<<}


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
