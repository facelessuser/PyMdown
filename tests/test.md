---
    settings:
        extensions:
        - extra
        - mdownx.github
        - mdownx.insert
        - toc
        - headerid
        - smarty
        - meta
        - wikilinks
        - admonition
        - codehilite(guess_lang=False,pygments_style=zenburn)
        - mdownx.b64(base_path=${BASE_PATH})
        - mdownx.absolutepath(base_path=${BASE_PATH})
---
!!! hint "Recommended Extentions for Testing"
    This is mainly used to test the Python Markdown parser.

    - extra
    - mdownx.github
    - mdownx.insert
    - toc
    - headerid
    - smarty
    - meta
    - footnotes
    - wikilinks
    - admonition
    - codehilite(guess_lang=False,pygments_style=github)
    - mdownx.b64(base_path=${BASE_PATH})
    - mdownx.absolutepath(base_path=${BASE_PATH})

    !!! Caution "Testing Note"
        - `sane_lists` will alter the results of the second test in [Mixed Lists](#mixed-lists). When turned off, this test will have all list items mixed and aligned proper.  With `sane_lists` on, some will not be recognized, and some items may be aligned in different lists.
        - having `guess_lang=False` allows the testing of the selective highlighting.  When omitted or set `true`, it can be expected that all of the blocks will be highlighted to some extent.
        - Most tests are spot checked at this point or a link can be clicked to verify it is working.
        - mdown.b64 check requires looking at the source of one of the images to see if conversion occured.


# Cheat Sheet and Test
[TOC]

## Headers

```
# H1
## H2
### H3
#### H4
##### H5
###### H6
### Duplicate Header
### Duplicate Header
```

# H1
## H2
### H3
#### H4
##### H5
###### H6
### Duplicate Header
### Duplicate Header

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
`inline block`

**bold 1** and __bold 2__

*italic 1*  and _italic 2_

~~strike~~


***bold 1 and italic 1***

___bold 2 and italic 2___

__*bold 2 and italic 1*__

**_bold 1 and italic 2_**


~~*strike italic 1*~~ and *~~strike italic 2~~*

~~_strike italic 2_~~ and  _~~strike italic 2~~_


~~**strike bold 1**~~ and **~~strike bold 1~~**

~~__strike bold 2__~~ and __~~strike bold 2~~__


~~***strike italic 1 bold 1***~~ and ***~~strike italic 1 bold 1~~***

~~___strike italic 2 bold 2___~~ and ___~~strike italic 2 bold 2~~___

**~~*strike italic 1 bold 1*~~** and *~~**strike italic 1 bold 1**~~*

__~~_strike italic 2 bold 2_~~__ and _~~__strike italic 2 bold 2__~~_

**~~_strike italic 2 bold 1_~~** and _~~**strike italic 2 bold 1**~~_

__~~*strike italic 1 bold 2*~~__ and *~~__strike italic 1 bold 2__~~*

```

`inline block`

**bold 1** and __bold 2__

*italic 1*  and _italic 2_

~~strike~~


***bold 1 and italic 1***

___bold 2 and italic 2___

__*bold 2 and italic 1*__

**_bold 1 and italic 2_**


~~*strike italic 1*~~ and *~~strike italic 2~~*

~~_strike italic 2_~~ and  _~~strike italic 2~~_


~~**strike bold 1**~~ and **~~strike bold 1~~**

~~__strike bold 2__~~ and __~~strike bold 2~~__


~~***strike italic 1 bold 1***~~ and ***~~strike italic 1 bold 1~~***

~~___strike italic 2 bold 2___~~ and ___~~strike italic 2 bold 2~~___

**~~*strike italic 1 bold 1*~~** and *~~**strike italic 1 bold 1**~~*

__~~_strike italic 2 bold 2_~~__ and _~~__strike italic 2 bold 2__~~_

**~~_strike italic 2 bold 1_~~** and _~~**strike italic 2 bold 1**~~_

__~~*strike italic 1 bold 2*~~__ and *~~__strike italic 1 bold 2__~~*


## Links
Footnote and reference sources are at the bottom of the page.
```
[Reference Link][1]

Footnotes[^1] have a label[^label] and a definition[^!DEF]

![A Picture](bg.png "A Picture")

[Link to Picture](bg.png "Link")

https://github.com/facelessuser/mdown

This is a link https://github.com/facelessuser/mdown.

This is a link "https://github.com/facelessuser/mdown".

With this link (https://github.com/facelessuser/mdown), it still works.

    [1]: https://github.com/facelessuser/mdown
    [^1]: This is a footnote
    [^label]: A footnote on "label"
    [^!DEF]: The footnote for definition
```

[Reference Link][1]

Footnotes[^1] have a label[^label] and a definition[^!DEF]

![A Picture](bg.png "A Picture")

[Link to Picture](bg.png "Link")

https://github.com/facelessuser/mdown

This is a link https://github.com/facelessuser/mdown.

This is a link "https://github.com/facelessuser/mdown".

With this link (https://github.com/facelessuser/mdown), it still works.

## Abbreviation
Abreviations source are found at the bottom of the page
```
The HTML specification 
is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]:  World Wide Web Consortium
```

The HTML specification 
is maintained by the W3C.

## Unordered List

```
Unordered List

- item 1
    * item A
    * item B
        more text
        + item a
        + item b
        + item c
    * item C
- item 2
- item 3
```

Unordered List

- item 1
    * item A
    * item B
        more text
        + item a
        + item b
        + item c
    * item C
- item 2
- item 3


## Ordered List
```
Ordered List

1. item 1
    1. item A
    2. item B
        more text
        1. item a
        2. item b
        3. item c
    3. item C
2. item 2
3. item 3
```

Ordered List

1. item 1
    1. item A
    2. item B
        more text
        1. item a
        2. item b
        3. item c
    3. item C
2. item 2
3. item 3

## Task List
```
Task List

- [X] item 1
    * [X] item A
    * [ ] item B
        more text
        + [x] item a
        + [ ] item b
        + [x] item c
    * [X] item C
- [ ] item 2
- [ ] item 3
```

Task List

- [X] item 1
    * [X] item A
    * [ ] item B
        more text
        + [x] item a
        + [ ] item b
        + [x] item c
    * [X] item C
- [ ] item 2
- [ ] item 3

## Mixed Lists
`Really Mixed Lists` should break with `sane_lists` on.

```
Mixed Lists

- item 1
    * [X] item A
    * [ ] item B
        more text
        1. item a
        2. itemb
        3. item c
    * [X] item C
- item 2
- item 3


Really Mixed Lists

- item 1
    * [X] item A
    - item B
        more text
        1. item a
        + itemb
        + [ ] item c
    3. item C
2. item 2
- [X] item 3
```

Mixed Lists

- item 1
    * [X] item A
    * [ ] item B
        more text
        1. item a
        2. itemb
        3. item c
    * [X] item C
- item 2
- item 3


Really Mixed Lists

- item 1
    * [X] item A
    - item B
        more text
        1. item a
        + itemb
        + [ ] item c
    3. item C
2. item 2
- [X] item 3


## Dictionary
```
Dictionary
:   item 1

    item 2

    item 3
```

Dictionary
:   item 1

    item 2

    item 3

## Blocks
```
    This is a block.
    
    This is more of a block.

```

    This is a block.
    
    This is more of a block.


## Block Quotes
```
> This is a block quote
>> How does it look?
```

> This is a block quote.
>> How does it look?
> I think it looks good.

## Fenced Block
Assuming guessing is not enabled.

`````
```
// Fenced **without** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i^^) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```

```javascript
// Fenced **with** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i^^) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```
`````

```
// Fenced **without** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i^^) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```

```javascript
// Fenced **with** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i^^) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```

## Tables

```
| _Colors_      | Fruits          | Vegetable         |
| ------------- |:---------------:| -----------------:|
| Red           | *Apple*         | [Pepper](#Tables) |
| ~~Orange~~    | Oranges         | **Carrot**        |
| Green         | ~~***Pears***~~ | Spinach           |
```

| _Colors_      | Fruits          | Vegetable    |
| ------------- |:---------------:| ------------:|
| Red           | *Apple*         | Pepper       |
| ~~Orange~~    | Oranges         | **Carrot**   |
| Green         | ~~***Pears***~~ | Spinach      |

## Smart Strong
```
Text with double__underscore__words.

__Strong__ still works.

__this__works__too__
```

Text with double__underscore__words.

__Strong__ still works.

__this__works__too__

## Smarty
```
"double quotes"

'single quotes'

da--sh

elipsis...
```

"double quotes"

'single quotes'

da--sh

elipsis...

## Admonition
```
!!! Attention "Success!"
    You can use inline ~~stuff~~ markup too!

!!! Hint "Info!"
    - Here is some info.
    - And some more

!!! Caution "Warning!"
    - [X] Make sure you turn off the stove
    - [X] Don't run with scissors

!!! Danger "Alert!"
    You really need to read [this](#admonition)!

!!! Note ""
    This one has no `title`.

    > Not all markup can be placed in these boxes, but you can fit all sorts of things in them. But you will notice that the styles don't always play nice with each other.  Additional CSS could fix this though.

    Stuff like _this_ works too.

    | _Colors_      | Fruits          | Vegetable    |
    | ------------- |:---------------:| ------------:|
    | Red           | *Apple*         | Pepper       |
    | ~~Orange~~    | Oranges         | **Carrot**   |
    | Green         | ~~***Pears***~~ | Spinach      |
```

!!! Attention "Success!"
    You can use inline ~~stuff~~ markup too!

!!! Hint "Info!"
    - Here is some info.
    - And some more

!!! Caution "Warning!"
    - [X] Make sure you turn off the stove
    - [X] Don't run with scissors

!!! Danger "Alert!"
    You really need to read [this](#admonition)!

!!! Note ""
    This one has no `title` :smile:.

    > Not all markup can be placed in these boxes, but you can fit all sorts of things in them. But you will notice that the styles don't always play nice with each other.  Additional CSS could fix this though.

    Stuff like _this_ works too.

    | _Colors_      | Fruits          | Vegetable    |
    | ------------- |:---------------:| ------------:|
    | Red           | *Apple*         | Pepper       |
    | ~~Orange~~    | Oranges         | **Carrot**   |
    | Green         | ~~***Pears***~~ | Spinach      |

## Github Emoji
```
This is a test for emoji :smile:.  The emojis are images linked to github assets :octocat:.
```

This is a test for emoji :smile:.  The emojis are images linked to github assets :octocat:.

## Insert
```
^^insert^^

^^*insert italic*^^  *^^insert italic 2^^*

^^_insert italic_^^  _^^insert italic 2^^_

^^**insert bold**^^  **^^insert bold 2^^**

^^__insert bold__^^  __^^insert bold 2^^__

^^***insert italic bold***^^  ***^^insert italic bold 2^^***

^^___insert italic bold___^^  ___^^insert italic bold 2^^___

**^^*insert italic bold*^^**  *^^**insert italic bold 2**^^*

__^^_insert italic bold_^^__  _^^__insert italic bold 2__^^_

**^^_insert italic bold_^^**  _^^**insert italic bold 2**^^_

__^^*insert italic bold*^^__  *^^__insert italic bold 2__^^*
```

^^insert^^

^^*insert italic*^^  *^^insert italic 2^^*

^^_insert italic_^^  _^^insert italic 2^^_

^^**insert bold**^^  **^^insert bold 2^^**

^^__insert bold__^^  __^^insert bold 2^^__

^^***insert italic bold***^^  ***^^insert italic bold 2^^***

^^___insert italic bold___^^  ___^^insert italic bold 2^^___

**^^*insert italic bold*^^**  *^^**insert italic bold 2**^^*

__^^_insert italic bold_^^__  _^^__insert italic bold 2__^^_

**^^_insert italic bold_^^**  _^^**insert italic bold 2**^^_

__^^*insert italic bold*^^__  *^^__insert italic bold 2__^^*

*[HTML]: Hyper Text Markup Language
*[W3C]:  World Wide Web Consortium

[1]: https://github.com/facelessuser/mdown

[^1]: This is a footnote
[^label]: A footnote on "label"
[^!DEF]: The footnote for definition
