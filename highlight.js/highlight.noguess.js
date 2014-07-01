function hljs_initNoGuessOnLoad() {
    addEventListener('DOMContentLoaded', hljs_initNoGuessHighlighting, false);
    addEventListener('load', hljs_initNoGuessHighlighting, false);
}

function hljs_initNoGuessHighlighting() {
    var elements = document.querySelectorAll('pre code');
    var length = elements.length;
    var i;
    var j;
    var classes;
    var m;
    var language;
    var obj;
    var code;
    var index;
    if (length > 0) {
        for (i = 0; i < length; i++) {
            code = elements[i]
            classes = code.className.split(' ');
            language = null;
            for (j=0; j < classes.length; j++) {
                isCode = new RegExp(/^language-([^\s]+)$/)
                m = isCode.exec(classes[j]);
                if (m) {
                    index = j;
                    language = m[1];
                    break;
                }
            }
            if (language) {
                obj = hljs.highlight(language, code.textContent, true)
                code.innerHTML = obj.value;
                classes[index] = "hljs " + obj.language;
                code.className = classes.join(" ");
                code.parentNode.className += " hljs";
            }
        }
    }
}

hljs_initNoGuessOnLoad();
