(function (doc) {
  function onReady(fn) {
    if (doc.addEventListener) {
      doc.addEventListener("DOMContentLoaded", fn);
    } else {
      doc.attachEvent("onreadystatechange", function() {
        if (doc.readyState === "interactive")
          fn();
      });
    }
  }

  onReady(function(){uml(Diagram, "uml-sequence-diagram", {theme: "simple"});});
})(document);
