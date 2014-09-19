"""
Reverse generated from CSS back to PY via pyg_css_convert.py
"""
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal


class SolarizedStyle(Style):
    background_color = "#002b36"  # Background
    highlight_color = "#ffffcc"   # <-- Not defined; defaulted

    styles = {
        Comment:                     "#586e75",
        Comment.Multiline:           "#586e75",
        Comment.Preproc:             "#859900",
        Comment.Single:              "#586e75",
        Comment.Special:             "#859900",
        Error:                       "#93a1a1",
        Generic:                     "#93a1a1",
        Generic.Deleted:             "#2aa198",
        Generic.Emph:                "italic #93a1a1",
        Generic.Error:               "#dc322f",
        Generic.Heading:             "#cb4b16",
        Generic.Inserted:            "#859900",
        Generic.Output:              "#93a1a1",
        Generic.Prompt:              "#93a1a1",
        Generic.Strong:              "bold #93a1a1",
        Generic.Subheading:          "#cb4b16",
        Generic.Traceback:           "#93a1a1",
        Keyword:                     "#859900",
        Keyword.Constant:            "#cb4b16",
        Keyword.Declaration:         "#268bd2",
        Keyword.Namespace:           "#859900",
        Keyword.Pseudo:              "#859900",
        Keyword.Reserved:            "#268bd2",
        Keyword.Type:                "#dc322f",
        Literal:                     "#93a1a1",
        Literal.Date:                "#93a1a1",
        Literal.Number:              "#2aa198",
        Literal.Number.Float:        "#2aa198",
        Literal.Number.Hex:          "#2aa198",
        Literal.Number.Integer:      "#2aa198",
        Literal.Number.Integer.Long: "#2aa198",
        Literal.Number.Oct:          "#2aa198",
        Literal.String:              "#2aa198",
        Literal.String.Backtick:     "#586e75",
        Literal.String.Char:         "#2aa198",
        Literal.String.Doc:          "#93a1a1",
        Literal.String.Double:       "#2aa198",
        Literal.String.Escape:       "#cb4b16",
        Literal.String.Heredoc:      "#93a1a1",
        Literal.String.Interpol:     "#2aa198",
        Literal.String.Other:        "#2aa198",
        Literal.String.Regex:        "#dc322f",
        Literal.String.Single:       "#2aa198",
        Literal.String.Symbol:       "#2aa198",
        Name:                        "#93a1a1",
        Name.Attribute:              "#93a1a1",
        Name.Builtin:                "#b58900",
        Name.Builtin.Pseudo:         "#268bd2",
        Name.Class:                  "#268bd2",
        Name.Constant:               "#cb4b16",
        Name.Decorator:              "#268bd2",
        Name.Entity:                 "#cb4b16",
        Name.Exception:              "#cb4b16",
        Name.Function:               "#268bd2",
        Name.Label:                  "#93a1a1",
        Name.Namespace:              "#93a1a1",
        Name.Other:                  "#93a1a1",
        Name.Property:               "#93a1a1",
        Name.Tag:                    "#268bd2",
        Name.Variable:               "#268bd2",
        Name.Variable.Class:         "#268bd2",
        Name.Variable.Global:        "#268bd2",
        Name.Variable.Instance:      "#268bd2",
        Operator:                    "#859900",
        Operator.Word:               "#859900",
        Other:                       "#cb4b16",
        Punctuation:                 "#93a1a1",
        Text:                        "#93a1a1",  # Foreground
        Text.Whitespace:             "#93a1a1"

        # Below are classes that could not be resolved:

        # Below are invalid rules:
    }
