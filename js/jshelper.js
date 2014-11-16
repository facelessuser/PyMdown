function onReady(fn) {
  if (document.addEventListener) {
    document.addEventListener('DOMContentLoaded', fn);
  } else {
    document.attachEvent('onreadystatechange', function() {
      if (document.readyState === 'interactive')
        fn();
    });
  }
}

function addClass(el, className) {
  if (el.classList)
    el.classList.add(className);
  else
    el.className += ' ' + className;
}

function removeClass(el, className)
{
  if (el.classList)
    el.classList.remove(className);
  else
    el.className = el.className.replace(new RegExp('(?:^|\s)' + className.split(' ') + '(?!\S)', 'g'), ' ');
}

function isUndef(obj) {
  return obj === void 0
}

function removeEvent(el, eventName, handler) {
  if (el.removeEventListener) {
    el.removeEventListener(eventName, handler);
  } else {
    el.detachEvent('on' + eventName, handler);
  }
}

function addEvent(el, eventName, handler) {
  if (el.addEventListener) {
    el.addEventListener(eventName, handler);
  } else {
    el.attachEvent(
        'on' + eventName,
        function(){handler.call(el);}
    );
  }
}

function isChildOf(parent, child) {
  while((child = child.parentNode) && child !== parent);
  return !!child;
}
