(function (doc) {
  function onReady(fn) {
    if (doc.addEventListener) {
      doc.addEventListener('DOMContentLoaded', fn);
    } else {
      doc.attachEvent('onreadystatechange', function() {
        if (doc.readyState === 'interactive')
          fn();
      });
    }
  }

  function isUndef(obj) {
    return obj === void 0;
  }

  function convertUML(className, converter, settings) {
    var charts = doc.querySelectorAll("pre." + className),
        arr = [],
        i, maxItem, diagaram, text, curNode;

    // Is there a settings object?
    if (isUndef(settings)) {
        settings = {};
    }

    // Make sure we are dealing with an array
    for(i = 0, maxItem = charts.length; i < maxItem; i++) arr.push(charts[i])

    // Find the UML source element and get the text
    for (i = 0, maxItem = arr.length; i < maxItem; i++) {
        childEl = arr[i].firstChild;
        parentEl = childEl.parentNode;
        text = "";
        for (var i = 0; i < childEl.childNodes.length; i++) {
            curNode = childEl.childNodes[i];
            whitespace = /^\s*$/;
            if (curNode.nodeName === "#text" && !(whitespace.test(curNode.nodeValue))) {
                text = curNode.nodeValue;
                break;
            }
        }

        // Do UML conversion and replace source
        el = doc.createElement('div');
        el.className = className;
        parentEl.parentNode.insertBefore(el, parentEl);
        parentEl.parentNode.removeChild(parentEl);
        diagram = converter.parse(text);
        diagram.drawSVG(el, settings);
    }
  }

  if (!isUndef(flowchart)) {
    onReady(function(){convertUML('uml-flow', flowchart);});
  }
  if (!isUndef(Diagram)) {
    onReady(function(){convertUML('uml-sequence', Diagram, {theme: 'simple'});});
  }
})(document)
