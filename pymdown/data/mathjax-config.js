(function (win, doc) {
  win.MathJax = {
    config: ["MMLorHTML.js"],
    jax: ["input/TeX", "output/HTML-CSS", "output/NativeMML"],
    extensions: ["tex2jax.js", "MathMenu.js", "MathZoom.js"],
    tex2jax: {
        inlineMath: [ ["\\(","\\)"] ],
        displayMath: [ ["\\[","\\]"] ]
    },
    TeX: {
        TagSide: "right",
        TagIndent: ".8em",
        MultLineWidth: "85%",
        equationNumbers: {
            autoNumber: "AMS",
        }
    },
    displayAlign: "left",
    showProcessingMessages: false,
    messageStyle: "none"
  };
})(window, document);
