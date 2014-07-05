"""
Reverse generated from CSS back to PY via pyg_css_convert.py
"""
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal


class ZenburnStyle(Style):
    background_color = "#3f3f3f"  # Background
    highlight_color = "#222222"   # Highlight Line

    styles = {
        Comment:                     "#7f9f7f",
        Comment.Multiline:           "#7f9f7f",
        Comment.Preproc:             "#7f9f7f",
        Comment.Single:              "#7f9f7f",
        Comment.Special:             "bold #cd0000",
        Error:                       "bg:#3d3535 #e37170",
        Generic:                     "#7f9f7f",
        Generic.Deleted:             "#cd0000",
        Generic.Emph:                "italic #cccccc",
        Generic.Error:               "#ff0000",
        Generic.Heading:             "bold #dcdccc",
        Generic.Inserted:            "#00cd00",
        Generic.Output:              "#808080",
        Generic.Prompt:              "bold #dcdccc",
        Generic.Strong:              "bold #cccccc",
        Generic.Subheading:          "bold #800080",
        Generic.Traceback:           "#0040d0",
        Keyword:                     "#f0dfaf",
        Keyword.Constant:            "#dca3a3",
        Keyword.Declaration:         "#ffff86",
        Keyword.Namespace:           "bold #dfaf8f",
        Keyword.Pseudo:              "#cdcf99",
        Keyword.Reserved:            "#cdcd00",
        Keyword.Type:                "#00cd00",
        Literal:                     "#cccccc",
        Literal.Date:                "#cc9393",
        Literal.Number:              "#8cd0d3",
        Literal.Number.Float:        "#8cd0d3",
        Literal.Number.Hex:          "#8cd0d3",
        Literal.Number.Integer:      "#8cd0d3",
        Literal.Number.Integer.Long: "#8cd0d3",
        Literal.Number.Oct:          "#8cd0d3",
        Literal.String:              "#cc9393",
        Literal.String.Backtick:     "#cc9393",
        Literal.String.Char:         "#cc9393",
        Literal.String.Doc:          "#cc9393",
        Literal.String.Double:       "#cc9393",
        Literal.String.Escape:       "#cc9393",
        Literal.String.Heredoc:      "#cc9393",
        Literal.String.Interpol:     "#cc9393",
        Literal.String.Other:        "#cc9393",
        Literal.String.Regex:        "#cc9393",
        Literal.String.Single:       "#cc9393",
        Literal.String.Symbol:       "#cc9393",
        Name:                        "#dcdccc",
        Name.Attribute:              "#9ac39f",
        Name.Builtin:                "#efef8f",
        Name.Builtin.Pseudo:         "#efef8f",
        Name.Class:                  "#efef8f",
        Name.Constant:               "#cccccc",
        Name.Decorator:              "#cccccc",
        Name.Entity:                 "#c28182",
        Name.Exception:              "bold #c3bf9f",
        Name.Function:               "#efef8f",
        Name.Label:                  "#cccccc",
        Name.Namespace:              "#8fbede",
        Name.Other:                  "#cccccc",
        Name.Property:               "#cccccc",
        Name.Tag:                    "#9ac39f",
        Name.Variable:               "#dcdccc",
        Name.Variable.Class:         "#efef8f",
        Name.Variable.Global:        "#dcdccc",
        Name.Variable.Instance:      "#ffffc7",
        Operator:                    "#f0efd0",
        Operator.Word:               "#f0efd0",
        Other:                       "#cccccc",
        Punctuation:                 "#41706f",
        Text:                        "#cccccc",  # Foreground
        Text.Whitespace:             "#cccccc"

        # Below are classes that could not be resolved:

        # Below are invalid rules:
    }
